import os
from dotenv import load_dotenv
load_dotenv()

# Environment variables
YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
YOUTUBE_API_SERVICE_NAME = os.environ['YOUTUBE_API_SERVICE_NAME']
YOUTUBE_API_VERSION = os.environ['YOUTUBE_API_VERSION']

#Google
GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET= os.environ['GOOGLE_CLIENT_SECRET']
GOOGLE_REDIRECT_URI= os.environ['GOOGLE_REDIRECT_URI']
SESSION_SECRET_KEY= os.environ['SESSION_SECRET_KEY']

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
