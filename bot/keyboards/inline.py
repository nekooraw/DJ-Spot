from urllib.parse import urlencode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import SPOTIFY_CLIENT_ID

SCOPES = (
    "user-read-private user-read-email "
    "user-read-currently-playing user-read-playback-state user-modify-playback-state "
    "playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative "
    "user-library-read user-library-modify "
    "user-top-read user-read-recently-played"
)

def get_spotify_auth_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:3434",
        "scope": SCOPES,
        "state": str(telegram_id)
    }

    spotify_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔑 Войти через Spotify", url=spotify_url)
        ]
    ])