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

    # Проверяем, есть ли информация о реакции (callback query)
    if 'callback_query' in data:
        callback_data = data["callback_query"]
        logging.info(f"Received callback query: {callback_data}")
        
        # Извлекаем эмоцию из callback_data
        if 'data' in callback_data:
            # Пример: reaction_emoji
            callback_data_split = callback_data['data'].split('_')
            if len(callback_data_split) == 2 and callback_data_split[0] == 'reaction':
                emoji = callback_data_split[1]
                chat_id = callback_data["message"]["chat"]["id"]
                user_id = callback_data["from"]["id"]

                # Получаем количество очков за эту эмоцию
                points = await get_emotion_points(chat_id, emoji)
                if points:
                    # Начисляем очки пользователю
                    await set_user_points(user_id, chat_id, points)
                    await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию с эмоцией '{emoji}'!")
                else:
                    await bot.send_message(chat_id, "Эта реакция не настроена для начисления очков.")

    # Проверка сообщений с эмоциями
    if 'message' in data:
        message_data = data['message']

        # Проверяем, есть ли эмоции в сообщении
        if 'entities' in message_data:
            for entity in message_data['entities']:
                if entity['type'] == 'emoji':
                    emoji = message_data['text'][entity['offset']:entity['offset'] + entity['length']]
                    chat_id = message_data['chat']['id']
                    user_id = message_data['from']['id']

                    # Проверяем, есть ли эта эмоция в базе данных
                    points = await get_emotion_points(chat_id, emoji)

                    if points and points > 0:
                        # Если эмоция найдена в базе, начисляем очки
                        await set_user_points(user_id, chat_id, points)
                        await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию с эмоцией '{emoji}'!")

    return {"status": "ok"}
