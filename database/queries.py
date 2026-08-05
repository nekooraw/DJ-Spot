import time
from database.db_connection import async_session, User


async def save_spotify_tokens(telegram_id: int, access_token: str, refresh_token: str, expires_in: int):
    async with async_session() as session:
        user = await session.get(User, telegram_id)

        if not user:
            user = User(telegram_id=telegram_id)
            session.add(user)

        user.access_token = access_token
        user.refresh_token = refresh_token
        user.expires_at = int(time.time()) + expires_in

        await session.commit()


