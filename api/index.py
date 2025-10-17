from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_video_id(url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Ось тут виправлення:
@app.get("/subtitles")
def get_subtitles(video_url: str = Query(..., description="URL of the YouTube video")):
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['uk', 'en', 'ru'])
        formatted_transcript = " ".join([item['text'] for item in transcript])
        return {"transcript": formatted_transcript}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Could not retrieve subtitles. Error: {str(e)}")

# Важливо: Vercel очікує, що головний файл в /api буде обробляти всі запити до /api/*
# Тому ми повертаємо сам FastAPI app, а Vercel вже розбереться з роутінгом.
# Для цього іноді потрібно додати обробник для кореневого шляху, якщо Vercel не справляється.
# Але у вашому випадку заміна шляху вище має вирішити проблему.
