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
    if 'callback_query' in data:
        callback_data = data["callback_query"]
        # Обрабатываем callback-запросы, если необходимо
        logging.info(f"Received callback query: {callback_data}")

    if 'message' in data:
        message_data = data['message']

        # Проверка, есть ли эмоции в сообщении
        if 'entities' in message_data:
            for entity in message_data['entities']:
                if entity['type'] == 'emoji':
                    emoji = entity['text']
                    chat_id = message_data['chat']['id']
                    user_id = message_data['from']['id']
                    
                    # Проверяем, есть ли эта эмоция в базе данных
                    points = await get_emotion_points(chat_id, emoji)
                    
                    if points > 0:
                        # Если эмоция найдена в базе, начисляем очки
                        await set_user_points(user_id, chat_id, points)
                        await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию с эмоцией {emoji}!")

    return {"status": "ok"}

