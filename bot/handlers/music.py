from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from services.spotify_client import SpotifyAuthError, SpotifyClient, SpotifyClientError

router = Router()


class MusicSearch(StatesGroup):
    waiting_for_query = State()


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("🎵 Введите название трека или имя исполнителя для поиска:")
    await state.set_state(MusicSearch.waiting_for_query)


@router.message(MusicSearch.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    telegram_id = message.from_user.id

    spotify = SpotifyClient(telegram_id=telegram_id)

    try:
        tracks = await spotify.search_tracks(query=query)

        if not tracks:
            await message.answer("❌ Ничего не найдено по вашему запросу. Попробуйте еще раз.")
            await state.clear()
            return

        response_text = f"🔍 **Результаты поиска по запросу:** *{query}*\n\n"
        inline_keyboard_buttons = []

        for idx, track in enumerate(tracks[:5], start=1):
            track_name = track.get("name", "Неизвестный трек")
            artists = ", ".join([artist.get("name") for artist in track.get("artists", [])])
            track_id = track.get("id")

            response_text += f"{idx}. **{artists}** — {track_name}\n"

            inline_keyboard_buttons.append(
                [InlineKeyboardButton(text=f"▶️ Включить №{idx}", callback_data=f"play_tr:{track_id}")]
            )

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard_buttons)
        await message.answer(response_text, reply_markup=keyboard, parse_mode="Markdown")

    except SpotifyAuthError:
        await message.answer("❌ Вы не авторизованы. Пожалуйста, введите /start, чтобы привязать аккаунт.")
    except SpotifyClientError as e:
        await message.answer(f"❌ Ошибка при работе со Spotify: {e}")
    finally:
        await state.clear()


@router.callback_query(F.data.startswith("play_tr:"))
async def handle_play_callback(callback: CallbackQuery):
    track_id = callback.data.split(":")[1]
    telegram_id = callback.from_user.id

    spotify = SpotifyClient(telegram_id=telegram_id)

    try:
        await spotify.start_playback(track_ids=[track_id])
        await callback.answer("▶️ Воспроизведение запущено на вашем устройстве!")
    except SpotifyClientError as e:
        await callback.answer(f"⚠️ Ошибка: {e}\nУбедитесь, что Spotify активен на ПК/телефоне.", show_alert=True)
    except Exception:  # noqa: BLE001
        await callback.answer(
            "⚠️ Не удалось запустить. Проверьте активность вашего приложения Spotify.", show_alert=True
        )
