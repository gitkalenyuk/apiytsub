from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Vercel шукає змінну з назвою "app"
app = FastAPI()

# Middleware для CORS залишаємо, це важливо
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

# Оскільки vercel.json перенаправляє сюди всі запити з "/api/",
# то наш ендпоінт має відповідати на "/subtitles"
# Повний шлях для фронтенда буде /api/subtitles
@app.get("/api/subtitles")
def get_subtitles(video_url: str = Query(..., description="URL of the YouTube video")):
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['uk', 'en', 'ru'])
        formatted_transcript = " ".join([item['text'] for item in transcript])
        return {"transcript": formatted_transcript}
    except Exception as e:
        # Повертаємо більш детальну помилку, якщо субтитрів немає
        if "No transcripts were found" in str(e):
             raise HTTPException(status_code=404, detail="For this video, subtitles in Ukrainian, English, or Russian were not found.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# Це необов'язково, але корисно для перевірки, чи працює API
@app.get("/api")
def read_root():
    return {"message": "API is working correctly!"}
