from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Важливо: шлях тепер '/', тому що Vercel вже обробив /api/subtitles
@app.get("/")
def get_subtitles_handler(video_url: str = Query(..., description="URL of the YouTube video")):
    
    ydl_opts = {
        'writesubtitles': True,      # Вказуємо, що потрібні субтитри
        'sublang': 'uk,en,ru',       # Мови, які нас цікавлять
        'skip_download': True,       # Не завантажувати саме відео
        'extract_flat': True,        # Просто отримати інформацію
        'outtmpl': '/tmp/%(id)s',     # Куди тимчасово зберегти файл (Vercel дозволяє писати в /tmp)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_id = info.get('id')

            # yt-dlp повертає словник з доступними субтитрами
            available_subs = info.get('subtitles', {})
            
            # Шукаємо потрібну нам мову
            target_lang = None
            for lang in ['uk', 'en', 'ru']:
                if lang in available_subs:
                    target_lang = lang
                    break

            if not target_lang:
                raise HTTPException(status_code=404, detail="Subtitles not found for requested languages.")

            # Отримуємо дані субтитрів (це буде список)
            subtitles_data = available_subs[target_lang]
            
            # Зазвичай це список словників, з яких нам потрібен лише текст
            full_text = " ".join(item.get('line', '') for item in subtitles_data if 'line' in item)
            
            # Якщо з якоїсь причини yt-dlp не повернув текст напряму, то це запасний варіант (малоймовірно)
            if not full_text:
                # Цей блок може не знадобитись, але він для надійності
                sub_info = ydl.extract_info(video_url, download=True)
                sub_file_path = f"/tmp/{video_id}.{target_lang}.json"
                with open(sub_file_path, 'r') as f:
                    data = json.load(f)
                    full_text = " ".join(event.get('segs', [{}])[0].get('utf8', '') for event in data.get('events', []))

            if not full_text.strip():
                 raise HTTPException(status_code=404, detail="Found subtitle track, but it was empty.")

            return {"transcript": full_text.strip()}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
