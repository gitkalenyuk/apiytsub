from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yt_dlp
import json
import re

# Vercel автоматично знайде цей клас 'handler' і використає його для обробки запитів
class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Додаємо CORS заголовок, щоб браузер дозволив запит
        self.send_header('Access-Control-Allow-Origin', '*')
        
        # Парсимо URL, щоб отримати параметр ?video_url=...
        query_components = parse_qs(urlparse(self.path).query)
        video_url = query_components.get('video_url', [None])[0]

        if not video_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': 'Параметр video_url відсутній'}).encode('utf-8'))
            return

        # Налаштування для yt-dlp, щоб отримати лише субтитри
        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': ['uk', 'en', 'ru'],
            'skip_download': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                # 'requested_subtitles' - це ключ, де yt-dlp зберігає знайдені субтитри
                requested_subtitles = info.get('requested_subtitles')
                
                if not requested_subtitles:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'detail': 'Субтитри для обраних мов не знайдено.'}).encode('utf-8'))
                    return
                
                # Беремо першу доступну мову з результату
                lang_code = next(iter(requested_subtitles))
                sub_data = requested_subtitles[lang_code]['data']

                # Очищуємо текст субтитрів від тайм-кодів та іншого сміття
                lines = sub_data.split('\n')
                text_lines = []
                for line in lines:
                    # Ігноруємо службові рядки формату VTT/SRT
                    if '-->' in line or re.match(r'^\d+$', line.strip()) or not line.strip() or 'WEBVTT' in line:
                        continue
                    # Видаляємо теги, як-от <c> або <i>
                    clean_line = re.sub(r'<[^>]+>', '', line)
                    text_lines.append(clean_line.strip())
                
                full_text = " ".join(text_lines)

                # Відправляємо успішну відповідь
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'transcript': full_text}).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'detail': f'Сталася помилка: {str(e)}'}).encode('utf-8'))
            
        return
