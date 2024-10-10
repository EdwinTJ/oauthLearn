# youtube.py
from googleapiclient.discovery import build

# Environment variables
from config import YOUTUBE_API_KEY,YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION

def get_video_comments(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

    # Get the comments
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=40
    ).execute()

    # Extract the comments, and store them in a list
    comments = []
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)

    return comments

def get_channel_videos(channel_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

    # Fetch the videos from the channel
    response = youtube.search().list(
        channelId=channel_id,
        part='id,snippet',
        maxResults=15,
        order='date'
    ).execute()

    # Parse the response and return videos
    videos = []
    for item in response['items']:
        video_data = {
            'title': item['snippet']['title'],
            'videoId': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'description': item['snippet']['description']
        }
        videos.append(video_data)

    return videos
