#webhook_server.py

from fastapi import FastAPI, Request
from aiogram import Bot
from config import BOT_TOKEN
import logging
from database.queries import get_emotion_points
from database.users import set_user_points

app = FastAPI()

bot = Bot(token=BOT_TOKEN)

@app.post("/webhook")
async def process_update(request: Request):
    data = await request.json()
    logging.info(f"Received webhook data: {data}")

    # Проверка сообщений с эмодзи (необходимо только, если нужно обрабатывать сообщения с эмодзи)
    if 'message' in data:
        message_data = data['message']

        # Проверяем, есть ли эмодзи в сообщении
        if 'entities' in message_data:
            for entity in message_data['entities']:
                if entity['type'] == 'emoji':  # Мы обрабатываем только эмодзи
                    emoji = message_data['text'][entity['offset']:entity['offset'] + entity['length']]
                    chat_id = message_data['chat']['id']
                    user_id = message_data['from']['id']  # Это ID пользователя, который отправил сообщение

                    # Получаем количество очков для этой эмоции из базы данных
                    points = await get_emotion_points(emoji, chat_id)

                    # Если эмоция найдена и за нее начисляются очки
                    if points and points > 0:
                        # Начисляем очки пользователю, который отправил сообщение
                        current_points = await set_user_points(user_id, chat_id)
                        new_points = current_points + points
                        await set_user_points(user_id, chat_id, new_points)
                        await bot.send_message(chat_id, f"Вы получили {points} очков за сообщение с эмоцией '{emoji}'!")

    return {"status": "ok"}
