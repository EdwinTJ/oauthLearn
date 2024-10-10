
### Not working
import json
import os
import pathlib
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse,RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
from starlette.middleware.sessions import SessionMiddleware
from urllib.parse import urlencode

# Load environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Allow HTTP traffic for local dev


flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost:8000/auth/callback"
)

@app.get("/auth/login")
async def login(request: Request):
    authorization_url, state = flow.authorization_url()
    request.session["state"] = state
    print(f"seesion {state}")
    return JSONResponse({"authorization_url": authorization_url, "state": state})


@app.get("/auth/callback")
@app.post("/auth/callback")
async def callback(request: Request):
    try:
        if request.method == "GET":
            state = request.query_params.get("state")
            code = request.query_params.get("code")
        else:
            body = await request.json()
            state = body.get("state")
            code = body.get("code")
        
        print(f"Received state: {state}")
        print(f"Received code: {code}")
        
        session_state = request.session.get("state")
        print(f"Session state: {session_state}")
        
        if state != session_state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        token_request = google.auth.transport.requests.Request()

        id_info = id_token.verify_oauth2_token(
            id_token=credentials.id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

      # Create user_info dictionary
        user_info = {
            "id": id_info.get("sub"),
            "name": id_info.get("name"),
            "email": id_info.get("email"),
        }

        # Update session
        request.session["google_id"] = id_info.get("sub")
        request.session["name"] = id_info.get("name")
        request.session["email"] = id_info.get("email") 

        if request.method == "GET":
            params = urlencode({
                "access_token": credentials.token,
                "google_id": json.dumps(id_info.get("sub")),
                "name": json.dumps(id_info.get("name")),
                "email": json.dumps(id_info.get("email") )
            })
            return RedirectResponse(f"{FRONTEND_URL}/auth/callback?{params}")
        else:
            return JSONResponse({
                "access_token": credentials.token,
                "user_info": user_info
            })

    except Exception as e:
        print(f"Error in callback: {str(e)}")
        if request.method == "GET":
            error_params = urlencode({"error": str(e)})
            return RedirectResponse(f"{FRONTEND_URL}/auth/callback?{error_params}")
        else:
            raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)