import httpx
import uvicorn
from fastapi import FastAPI, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from services.spotify_client import SpotifyAuthError, SpotifyClient

app = FastAPI(
    title="DJ-Spot OAuth Server",
    description="Веб-сервер для обработки авторизации пользователей через Spotify API",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def spotify_callback(code: str = Query(...), state: str = Query(...)):
    try:
        telegram_id = int(state)
    except ValueError:
        return HTMLResponse(
            content="<h1>Ошибка: Неверный идентификатор пользователя (state).</h1>",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    spotify = SpotifyClient(telegram_id=telegram_id)

    async with httpx.AsyncClient() as http_client:
        spotify.client = http_client

        try:
            await spotify.exchange_code(code=code)
        except SpotifyAuthError as e:
            return HTMLResponse(
                content=f"<h1>Ошибка авторизации в Spotify:</h1><p>{e}</p>", status_code=status.HTTP_400_BAD_REQUEST
            )

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Авторизация DJ-Spot успешно завершена</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #FFFFFF;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #181818;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                text-align: center;
                max-width: 450px;
            }
            h1 {
                color: #1DB954;
                margin-bottom: 15px;
                font-size: 36px;
            }
            p {
                color: #E5E5E5;
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 20px;
            }
            .anime-img {
                width: 100%;
                max-width: 280px;
                border-radius: 12px;
                margin-bottom: 25px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.4);
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #1DB954;
                color: white;
                text-decoration: none;
                border-radius: 30px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: #1ed760;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Успешно!</h1>
            <p>Ваш аккаунт Spotify успешно привязан к боту <b>DJ-Spot</b>.</p>
            
            <img class="anime-img" src="/static/yui_happy.gif" alt="Yui Hirasawa Happy">
            
            <p>Теперь вы можете закрыть эту вкладку браузера и вернуться в Telegram.</p>
            
            <a href="https://t.me/DJ_Spot_music_bot" class="btn">Вернуться в Telegram</a>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=status.HTTP_200_OK)


@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    html_404 = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Страница не найдена | DJ-Spot</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #FFFFFF;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background-color: #181818;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                text-align: center;
                max-width: 450px;
            }
            h1 {
                color: #FF5555;
                font-size: 64px;
                margin: 0 0 10px 0;
            }
            p {
                color: #E5E5E5;
                font-size: 18px;
                line-height: 1.5;
                margin-bottom: 20px;
            }
            .anime-img {
                width: 100%;
                max-width: 280px;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 6px 16px rgba(0,0,0,0.4);
            }
            .support-link {
                color: #1DB954;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.2s;
            }
            .support-link:hover {
                color: #1ed760;
                text-decoration: underline;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                background-color: #1DB954;
                color: white;
                text-decoration: none;
                border-radius: 30px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            .btn:hover {
                background-color: #1ed760;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>404</h1>
            <p>Упс! Кажется, Юи запуталась в проводах и потеряла эту страницу...</p>
            
            <img class="anime-img" src="/static/yui_cry.png" alt="Yui Hirasawa Crying">
            
            <div style="margin-bottom: 25px; font-size: 14px; color: #B3B3B3;">
                🛠 Проблемы? Написать: 
                <a href="https://t.me/nekooraw" class="support-link" style="display:inline; margin:0;">Админ 1</a> 
                | 
                <a href="https://t.me/eco1kd" class="support-link" style="display:inline; margin:0;">Админ 2</a>
            </div>
            
            <a href="https://t.me/DJ_Spot_music_bot" class="btn">Вернуться к Боту</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_404, status_code=404)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=3434, reload=True)
