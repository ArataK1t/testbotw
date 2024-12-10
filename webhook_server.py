#webhook_server.py

from fastapi import FastAPI, Request
from aiogram import Bot
from config import BOT_TOKEN
import logging
from database.queries import get_emotion_points
from database.users import set_user_points
from aiogram.types import CallbackQuery

app = FastAPI()

bot = Bot(token=BOT_TOKEN)

@app.post("/webhook")
async def process_update(request: Request):
    data = await request.json()
    logging.info(f"Received webhook data: {data}")

    # Обрабатываем данные о реакции на сообщение
    if 'message' in data:
        message_data = data['message']

        # Проверяем, есть ли реакции
        if 'reactions' in message_data:
            for reaction in message_data['reactions']:
                emoji = reaction['emoji']
                chat_id = message_data['chat']['id']
                user_id = message_data['from']['id']

                # Получаем количество очков за эмоцию
                points = await get_emotion_points(emoji, chat_id)
                if points:
                    # Начисляем очки
                    await set_user_points(user_id, chat_id, points)
                    await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию с эмоцией '{emoji}'.")
                else:
                    await bot.send_message(chat_id, "Эта реакция не настроена для начисления очков.")

    return {"status": "ok"}
