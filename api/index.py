from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pytube import YouTube
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
        r'(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# --- ЗМІНА ТУТ ---
# Шлях тепер просто "/subtitles", тому що vercel.json вже додав "/api/"
@app.get("/subtitles")
def get_subtitles(video_url: str = Query(..., description="URL of the YouTube video")):
    if not extract_video_id(video_url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
    try:
        yt = YouTube(video_url)
        
        caption = yt.captions.get_by_language_code('uk') or \
                  yt.captions.get_by_language_code('en') or \
                  yt.captions.get_by_language_code('ru') or \
                  yt.captions.get_by_language_code('a.uk')

        if not caption:
            raise HTTPException(
                status_code=404, 
                detail="Subtitles in Ukrainian, English, or Russian were not found for this video."
            )
            
        srt_captions = caption.generate_srt_captions()
        
        lines = srt_captions.split('\n')
        text_lines = [line for line in lines if not line.isdigit() and '-->' not in line and line.strip() != '']
        formatted_transcript = " ".join(text_lines)

        return {"transcript": formatted_transcript}

    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {str(e)}"
        )

# --- І ТУТ ТЕЖ ЗМІНА ---
# Тестовий ендпоінт для /api/
@app.get("/")
def read_root():
    return {"message": "API is working correctly! Send requests to /subtitles"}
