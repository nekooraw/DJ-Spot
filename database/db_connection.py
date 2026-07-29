import datetime
from sqlalchemy import BigInteger, String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///dj_spot.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'


    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    spotify_id: Mapped[str | None] = mapped_column(String, nullable=True, default=None)

    display_name: Mapped[str | None] = mapped_column(String, nullable=True, default=None)  # Имя в Spotify
    followers: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)  # Количество подписчиков
    country: Mapped[str | None] = mapped_column(String, nullable=True, default=None)  # Страна аккаунта
    email: Mapped[str | None] = mapped_column(String, nullable=True, default=None)  # Электронная почта
    product: Mapped[str | None] = mapped_column(String, nullable=True, default=None)  # Тип подписки (premium/free)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    access_token: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    refresh_token: Mapped[str | None] = mapped_column(String, nullable=True, default=None)
    expires_at: Mapped[int | None] = mapped_column(Integer, nullable=True, default=None)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
