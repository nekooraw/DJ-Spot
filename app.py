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
        <title>Успешно | DJ-Spot</title>
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background-color: #0b0b0e;
                color: #f3f4f6;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: #13131a;
                border: 1px solid #22222c;
                padding: 40px;
                border-radius: 24px;
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            h1 {
                color: #1DB954;
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 12px;
                letter-spacing: -0.5px;
            }
            p {
                color: #9ca3af;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 28px;
            }
            .anime-img {
                width: 160px;
                height: 160px;
                border-radius: 50%;
                margin-bottom: 28px;
                object-fit: cover;
                border: 2px solid #22222c;
            }
            .btn {
                display: block;
                width: 100%;
                padding: 14px;
                background-color: #1f1f2e;
                color: #ffffff;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #333344;
                transition: all 0.2s ease;
            }
            .btn:hover {
                background-color: #2b2b3d;
                border-color: #1DB954;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Успешно</h1>
            <p>Аккаунт Spotify привязан к боту <b>DJ-Spot</b>.</p>
            <img class="anime-img" src="/static/yui_happy.gif" alt="Success">
            <p>Теперь вы можете закрыть эту вкладку и вернуться в мессенджер.</p>
            <a href="https://t.me" class="btn">Открыть бота</a>
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
        <title>404 | DJ-Spot</title>
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                background-color: #0b0b0e;
                color: #f3f4f6;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
            }
            .card {
                background: #13131a;
                border: 1px solid #2c1a1a;
                padding: 40px;
                border-radius: 24px;
                text-align: center;
                max-width: 400px;
                width: 100%;
            }
            h1 {
                color: #ff4f4f;
                font-size: 56px;
                font-weight: 800;
                margin-bottom: 4px;
            }
            p {
                color: #9ca3af;
                font-size: 14px;
                line-height: 1.6;
                margin-bottom: 28px;
            }
            .anime-img {
                width: 160px;
                height: 160px;
                border-radius: 50%;
                margin-bottom: 28px;
                object-fit: cover;
                border: 2px solid #22222c;
            }
            .btn {
                display: block;
                width: 100%;
                padding: 14px;
                background-color: #1f1f2e;
                color: #ffffff;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
                border: 1px solid #333344;
                transition: all 0.2s ease;
            }
            .btn:hover {
                background-color: #2b2b3d;
                border-color: #ff4a4a;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>404</h1>
            <p>Страница не найдена. Юи запуталась в проводах...</p>
            <img class="anime-img" src="/static/yui_cry.png" alt="Error">
            <a href="https://t.me" class="btn">Вернуться к Боту</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_404, status_code=404)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=3434, reload=True)
