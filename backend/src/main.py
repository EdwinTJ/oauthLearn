from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
import os
from pydantic import BaseModel

# Load environment variables
from config import (
    YOUTUBE_API_KEY,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    SESSION_SECRET_KEY,
    GOOGLE_REDIRECT_URI,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP traffic for local dev

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [GOOGLE_REDIRECT_URI],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=SCOPES,
    redirect_uri=GOOGLE_REDIRECT_URI
)

class UserData(BaseModel):
    name: str
    email: str
    channel_id: str
    access_token: str
    refresh_token: str

user_data_store = {}  # In-memory storage, replace with a database in production

@app.get("/auth/login")
def login_with_google():
    authorization_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def auth_callback(code: str):
    flow.fetch_token(code=code)
    credentials = flow.credentials

    user_info_service = build("oauth2", "v2", credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    email = user_info["email"]
    name = user_info["name"]

    youtube_service = build("youtube", "v3", credentials=credentials)
    channel_response = youtube_service.channels().list(mine=True, part="snippet,contentDetails").execute()

    if not channel_response.get("items"):
        raise HTTPException(status_code=404, detail="No YouTube channel found")

    channel_id = channel_response["items"][0]["id"]

    user_data = UserData(
        name=name,
        email=email,
        channel_id=channel_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token
    )
    user_data_store[email] = user_data

    redirect_url = f"http://localhost:5173/?name={name}&email={email}&channel_id={channel_id}&access_token={credentials.token}"
    return RedirectResponse(redirect_url)

def refresh_access_token(refresh_token):
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    credentials.refresh(GoogleRequest())
    return credentials.token

@app.post("/api/refresh_token")
async def refresh_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    old_token = auth_header.split(" ")[1]
    user_data = next((u for u in user_data_store.values() if u.access_token == old_token), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        new_access_token = refresh_access_token(user_data.refresh_token)
        user_data.access_token = new_access_token
        return JSONResponse(content={"access_token": new_access_token})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Token refresh failed")
    
@app.get("/api/videos")
async def get_videos(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]
    user_data = next((u for u in user_data_store.values() if u.access_token == token), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        credentials = Credentials(
            token=user_data.access_token,
            refresh_token=user_data.refresh_token,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token"
        )

        youtube_service = build("youtube", "v3", credentials=credentials)
        video_response = youtube_service.search().list(part="snippet", channelId=user_data.channel_id, maxResults=10).execute()
        videos = video_response.get("items", [])

        return JSONResponse(content={"videos": videos})
    except Exception as e:
        # If there's an error, it might be due to an expired token
        # The frontend will handle this and attempt a token refresh
        raise HTTPException(status_code=401, detail="Token may have expired")

@app.get("/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        user_data = next((u for u in user_data_store.values() if u.access_token == token), None)
        if user_data:
            del user_data_store[user_data.email]
    return JSONResponse(content={"message": "Logged out successfully"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level="debug")