from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests_oauthlib.oauth2_session import OAuth2Session
import os
from pydantic import BaseModel
from typing import List
from datetime import datetime
#Open AI
import openai
from openai import OpenAI
from open_ai import summarize_comments as openai_summarize_comments
# Load environment variables
from config import (
    YOUTUBE_API_KEY,
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    SESSION_SECRET_KEY,
    GOOGLE_REDIRECT_URI,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_CLIENT_ID,
    OPENAI_API_KEY
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
    "https://www.googleapis.com/auth/youtube.force-ssl",
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
    token_expiry: datetime

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
        refresh_token=credentials.refresh_token,
        token_expiry=credentials.expiry
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
    return credentials.token, credentials.expiry

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
        new_access_token, expiry = refresh_access_token(user_data.refresh_token)
        user_data.access_token = new_access_token
        user_data.token_expiry = datetime.utcnow() + expiry
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
        video_response = youtube_service.search().list(
            part="snippet",
            channelId=user_data.channel_id,
            maxResults=15,
            order="date",
            type="video"
        ).execute()

        videos = [{
            'title': item['snippet']['title'],
            'videoId': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'description': item['snippet']['description']
        } for item in video_response.get('items', [])]

        return JSONResponse(content={"videos": videos})
    except Exception as e:
        # If there's an error, it might be due to an expired token
        # The frontend will handle this and attempt a token refresh
        raise HTTPException(status_code=401, detail="Token may have expired")

@app.get("/api/user")
async def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]
    user_data = next((u for u in user_data_store.values() if u.access_token == token), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    return JSONResponse(content={
        "name": user_data.name,
        "email": user_data.email,
        "channel_id": user_data.channel_id
    })

@app.get("/api/video/{video_id}/comments")
async def get_video_comments(video_id: str, request: Request):
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
        comments_response = youtube_service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=40
        ).execute()

        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] 
                    for item in comments_response.get('items', [])]

        return JSONResponse(content={"comments": comments})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to fetch comments")

@app.post("/api/summarize_comments")
async def summarize_comments(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    
    token = auth_header.split(" ")[1]
    user_data = next((u for u in user_data_store.values() if u.access_token == token), None)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    body = await request.json()
    video_id = body.get("video_id")
    prompt = body.get("prompt")

    if not video_id or not prompt:
        raise HTTPException(status_code=400, detail="Missing video_id or prompt")

    try:
        # Fetch comments
        credentials = Credentials(
            token=user_data.access_token,
            refresh_token=user_data.refresh_token,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token"
        )

        youtube_service = build("youtube", "v3", credentials=credentials)
        comments_response = youtube_service.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=40
        ).execute()

        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] 
                    for item in comments_response.get('items', [])]

        if not comments:
            return JSONResponse(content={"summary": "No comments found for this video."})

        # Summarize comments
        try:
            summary = openai_summarize_comments(comments, prompt)
            return JSONResponse(content={"summary": summary})
        except openai.APIError as e:
            print(f"OpenAI API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
        except Exception as e:
            print(f"Error in summarize_comments: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in summarize_comments: {str(e)}")

        except HttpError as e:
            if e.resp.status == 403 and "insufficientPermissions" in str(e):
                raise HTTPException(status_code=403, detail="Insufficient authentication scopes. Please log in again.")
            raise HTTPException(status_code=400, detail=f"YouTube API error: {str(e)}")
    except Exception as e:
        print(f"Error in summarize_comments endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to summarize comments: {str(e)}")

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