# DJ-Spot

Telegram-бот для поиска треков и работы с плейлистами Spotify. Показывает подборки, ищет музыку и сохраняет вкусы пользователя в базе.

> 🚧 Проект в разработке, функционал пока не реализован.

## Возможности

- Поиск треков через Spotify API
- Просмотр и получение плейлистов/подборок
- Сохранение пользователей и их лайков в PostgreSQL
- Инлайн и обычная клавиатура для навигации

## Стек

- Python 3.x
- aiogram — Telegram Bot API
- Spotify Web API (через `services/spotify_client.py`)
- PostgreSQL + psycopg2
- python-dotenv для конфигурации

## Структура проекта

```
dj_spot_bot/
│
├── bot/                        Telegram-интерфейс
│   ├── handlers/                Обработчики команд и кнопок
│   │   ├── common.py             /start, /help, главное меню
│   │   └── music.py              Поиск треков, плейлисты
│   └── keyboards/               Клавиатуры
│       ├── inline.py             Инлайн-кнопки
│       └── reply.py              Reply-клавиатура
│
├── services/                   Работа со Spotify API
│   └── spotify_client.py         Поиск треков, подборки
│
├── database/                   PostgreSQL
│   ├── db_connection.py          Подключение к БД
│   └── queries.py                SQL-запросы (юзеры, лайки)
│
├── config.py                   Конфигурация из .env
├── main.py                     Точка входа
├── .env                        Секреты (не в git)
├── .gitignore
└── requirements.txt
```

## Установка

```bash
git clone https://github.com/nekooraw/DJ-Spot.git
cd DJ-Spot
python -m venv venv
source venv/bin/activate - Linux, Mac
.\venv\Scripts\activate.bat - Windows cmd
.\venv\Scripts\Activate.ps1 - Windows PowerShell
pip install -r requirements.txt
```

## Конфигурация

Создай `.env` в корне проекта:

```
BOT_TOKEN=

SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=

DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

- `BOT_TOKEN` — получить у @BotFather
- `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET` — из Spotify Developer Dashboard

## Запуск

```bash
python main.py
```

## Лицензия

MIT
