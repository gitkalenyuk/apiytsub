document.getElementById('getSubsBtn').addEventListener('click', async () => {
    const videoUrl = document.getElementById('videoUrl').value.trim();
    const subtitleOutput = document.getElementById('subtitleOutput');
    const loader = document.getElementById('loader');

    if (!videoUrl) {
        subtitleOutput.textContent = 'Будь ласка, вставте посилання на відео.';
        return;
    }

    // Показуємо завантажувач і чистимо попередній результат
    loader.style.display = 'block';
    subtitleOutput.textContent = '';

    try {
        // Формуємо URL для запиту до нашого API
        // Коли проєкт на Vercel, шлях буде відносним /api/subtitles
        const apiUrl = `/api/subtitles?video_url=${encodeURIComponent(videoUrl)}`;
        
        const response = await fetch(apiUrl);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Не вдалося отримати субтитри.');
        }

        const data = await response.json();
        subtitleOutput.textContent = data.transcript;

    } catch (error) {
        subtitleOutput.textContent = `Помилка: ${error.message}`;
    } finally {
        // Ховаємо завантажувач
        loader.style.display = 'none';
    }
});