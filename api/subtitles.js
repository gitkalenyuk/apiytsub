// Імпортуємо потрібну функцію з бібліотеки
const { getCaptions } = require('youtube-captions-scraper');

// Функція для витягування ID відео з URL
const extractVideoId = (url) => {
  const patterns = [
    /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
    /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})/,
  ];
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return match[1];
    }
  }
  return null;
};

// Це головна функція, яку Vercel буде запускати.
// Вона автоматично стане доступною за адресою /api/subtitles
module.exports = async (req, res) => {
  // Додаємо CORS заголовки, щоб фронтенд міг робити запити
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  
  // Якщо це OPTIONS запит (браузер перевіряє доступ), просто відповідаємо успіхом
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const { video_url } = req.query; // Отримуємо параметр ?video_url=...

    if (!video_url) {
      return res.status(400).json({ detail: 'Параметр video_url відсутній' });
    }

    const videoId = extractVideoId(video_url);

    if (!videoId) {
      return res.status(400).json({ detail: 'Неправильний URL відео YouTube' });
    }
    
    // Отримуємо субтитри для української або англійської мови
    const captions = await getCaptions({ videoID: videoId, lang: 'uk' })
      .catch(() => getCaptions({ videoID: videoId, lang: 'en' }))
      .catch(() => getCaptions({ videoID: videoId, lang: 'ru' }));

    // Форматуємо масив субтитрів в один рядок
    const formattedTranscript = captions.map(item => item.text).join(' ');

    // Відправляємо успішну відповідь
    res.status(200).json({ transcript: formattedTranscript });

  } catch (error) {
    // Якщо субтитри не знайдено або сталася інша помилка
    res.status(404).json({ detail: 'Субтитри для цього відео не знайдено або сталася помилка.' });
  }
};
