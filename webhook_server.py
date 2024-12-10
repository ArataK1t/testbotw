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

    # Проверяем, есть ли информация о реакции
    if 'reaction' in data:
        reaction_data = data["reaction"]
        logging.info(f"Received reaction data: {reaction_data}")

        emotion = reaction_data['emoji']  # Эмоция (например, "thumbs_up")
        chat_id = reaction_data["message"]["chat"]["id"]
        user_id = reaction_data["user"]["id"]

        # Получаем количество очков за эту эмоцию из базы данных
        points = await get_emotion_points(emotion, chat_id)
        if points:
            # Получаем текущие очки пользователя
            current_points = await set_user_points(user_id, chat_id)
            new_points = current_points + points
            await set_user_points(user_id, chat_id, new_points)
            await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию с эмоцией '{emotion}'!")
        else:
            await bot.send_message(chat_id, f"Эта реакция с эмоцией '{emotion}' не настроена для начисления очков.")

    return {"status": "ok"}
