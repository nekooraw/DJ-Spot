import base64
import time

import httpx

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from database.db_connection import User, async_session
from database.queries import save_spotify_tokens


class SpotifyAuthError(Exception):
    pass


class SpotifyClientError(Exception):
    pass


AUTH_URL = "https://accounts.spotify.com"
API_URL = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        self._access_token: str | None = None
        self._expires_at: int = 0

    # авторизация

    @staticmethod
    def _auth_header() -> str:
        credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    @staticmethod
    def auth_url(state: str, scope: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_id": SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "scope": scope,
            "state": state,
        }
        return f"{AUTH_URL}/authorize?{urlencode(params)}"

    async def exchange_code(self, code: str):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AUTH_URL}/api/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": SPOTIFY_REDIRECT_URI,
                    "client_id": SPOTIFY_CLIENT_ID,
                    "client_secret": SPOTIFY_CLIENT_SECRET,
                },
            )

        if resp.status_code != 200:
            raise SpotifyAuthError(f"Ошибка обмена кода: {resp.status_code} — {resp.text}")

        data = resp.json()
        await save_spotify_tokens(
            self.telegram_id,
            data["access_token"],
            data["refresh_token"],
            data["expires_in"],
        )
        self._access_token = data["access_token"]
        self._expires_at = int(time.time()) + data["expires_in"]

    async def _refresh(self):
        async with async_session() as session:
            user = await session.get(User, self.telegram_id)
            if not user or not user.refresh_token:
                raise SpotifyAuthError("Refresh-токен не найден. Нужна повторная авторизация.")
            refresh_token = user.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AUTH_URL}/api/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": SPOTIFY_CLIENT_ID,
                    "client_secret": SPOTIFY_CLIENT_SECRET,
                },
            )

        data = resp.json()
        new_refresh = data.get("refresh_token", refresh_token)
        await save_spotify_tokens(
            self.telegram_id,
            data["access_token"],
            new_refresh,
            data.get("expires_in", 3600),
        )
        self._access_token = data["access_token"]
        self._expires_at = int(time.time()) + data.get("expires_in", 3600)

    async def _get_access_token(self) -> str:
        if not self._access_token or time.time() >= self._expires_at:
            await self._refresh()
        return self._access_token

    # низкоуровневый запрос

    async def _request(self, method, path, params=None, json=None):
        token = await self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient() as client:
            resp = await client.request(method, f"{API_URL}{path}", params=params, json=json, headers=headers)

        if resp.status_code == 401:
            self._access_token = None
            self._expires_at = 0
            return await self._request(method, path, params, json)

        if resp.status_code == 403:
            raise SpotifyClientError("Недостаточно прав (скорее всего, нет Premium).")

        if resp.status_code == 429:
            raise SpotifyClientError("Слишком много запросов к Spotify API. Подожди немного.")

        if resp.status_code >= 400:
            raise SpotifyClientError(f"Ошибка API: {resp.status_code} — {resp.text}")

        return resp.json() if resp.content else None

    # профиль

    async def get_profile(self) -> dict:
        profile = await self._request("GET", "/me")

        async with async_session() as session:
            user = await session.get(User, self.telegram_id)
            if user:
                user.spotify_id = profile.get("id")
                user.display_name = profile.get("display_name")
                user.followers = profile.get("followers", {}).get("total")
                user.country = profile.get("country")
                user.email = profile.get("email")
                user.product = profile.get("product")
                await session.commit()

        return profile

    # поиск

    async def search_tracks(self, query: str, limit: int = 10, offset: int = 0):
        data = await self._request(
            "GET",
            "/search",
            params={"q": query, "type": "track", "limit": limit, "offset": offset},
        )
        return data.get("tracks", {}).get("items", [])

    async def search_artists(self, query: str, limit: int = 10):
        data = await self._request(
            "GET",
            "/search",
            params={"q": query, "type": "artist", "limit": limit},
        )
        return data.get("artists", {}).get("items", [])

    async def search_albums(self, query: str, limit: int = 10):
        data = await self._request(
            "GET",
            "/search",
            params={"q": query, "type": "album", "limit": limit},
        )
        return data.get("albums", {}).get("items", [])

    async def search_playlists(self, query: str, limit: int = 10):
        data = await self._request(
            "GET",
            "/search",
            params={"q": query, "type": "playlist", "limit": limit},
        )
        return data.get("playlists", {}).get("items", [])

    # треки

    async def get_track(self, track_id: str) -> dict:
        return await self._request("GET", f"/tracks/{track_id}")

    async def get_top_tracks(self, limit: int = 10, time_range: str = "medium_term"):
        data = await self._request(
            "GET",
            "/me/top/tracks",
            params={"limit": limit, "time_range": time_range},
        )
        return data.get("items", [])

    async def get_currently_playing(self) -> dict | None:
        return await self._request("GET", "/me/player/currently-playing")

    # плейлисты

    async def get_playlist(self, playlist_id: str) -> dict:
        return await self._request("GET", f"/playlists/{playlist_id}")

    async def get_playlist_tracks(self, playlist_id: str, limit: int = 50, offset: int = 0):
        data = await self._request(
            "GET",
            f"/playlists/{playlist_id}/tracks",
            params={"limit": limit, "offset": offset},
        )
        return data.get("items", [])

    async def create_playlist(self, user_id: str, name: str, description: str = "", public: bool = True) -> dict:
        return await self._request(
            "POST",
            f"/users/{user_id}/playlists",
            json={"name": name, "description": description, "public": public},
        )

    async def add_tracks_to_playlist(self, playlist_id: str, track_ids: list[str]) -> dict:
        return await self._request(
            "POST",
            f"/playlists/{playlist_id}/tracks",
            json={"uris": [f"spotify:track:{tid}" for tid in track_ids]},
        )

    # управление воспроизведением

    async def start_playback(self, track_ids: list[str]):
        uris = [f"spotify:track:{tid}" for tid in track_ids]
        return await self._request("PUT", "/me/player/play", json={"uris": uris})

    async def pause_playback(self):
        return await self._request("PUT", "/me/player/pause")

    async def next_track(self):
        return await self._request("POST", "/me/player/next")
