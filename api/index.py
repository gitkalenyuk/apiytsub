from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Ініціалізуємо наш додаток
app = FastAPI()

# Додаємо middleware для CORS, щоб фронтенд міг робити запити до нас
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких джерел
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функція для витягування ID відео з URL
def extract_video_id(url):
    # Патерн для стандартних та коротких посилань YouTube
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Створюємо головний endpoint нашого API
@app.get("/api/subtitles")
def get_subtitles(video_url: str = Query(..., description="URL of the YouTube video")):
    video_id = extract_video_id(video_url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL provided.")
        
    try:
        # Отримуємо транскрипт (субтитри)
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['uk', 'en', 'ru'])
        
        # Форматуємо текст в один рядок
        formatted_transcript = " ".join([item['text'] for item in transcript])
        
        return {"transcript": formatted_transcript}
    except Exception as e:
        # Якщо субтитрів немає або сталась помилка
        raise HTTPException(status_code=404, detail=f"Could not retrieve subtitles. Error: {str(e)}")