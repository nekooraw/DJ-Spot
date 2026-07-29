import time
from sqlalchemy import select
from database.db_connection import async_session, User


async def save_spotify_tokens(telegram_id: int, access_token: str, refresh_token: str, expires_in: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if user:
            user.access_token = access_token
            user.refresh_token = refresh_token
            user.expires_at = int(time.time()) + expires_in

            await session.commit()
            return True

        return False
