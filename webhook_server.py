from fastapi import FastAPI, Request
from aiogram import Bot
from database.queries import get_emotion_points  # Функция для получения очков за эмоцию
from database.users import set_user_points  # Функция для обновления очков пользователя
from handlers.creator_handlers import get_user_points
from config import BOT_TOKEN

app = FastAPI()

bot = Bot(token=BOT_TOKEN)

@app.post("/webhook")
async def process_update(request: Request):
    # Получаем данные из запроса от Telegram
    data = await request.json()
    
    # Логируем полученные данные (для отладки)
    print(f"Received update: {data}")
    
    # Проверка, что в данных есть сообщение
    if "message" in data:
        message_data = data["message"]
        user_id = message_data['from']['id']
        chat_id = message_data['chat']['id']
        
        # Проверяем, если сообщение содержит сущности (например, смайлики или эмоции)
        if 'entities' in message_data:
            for entity in message_data['entities']:
                if entity.type == 'emoji':  # Если сущность это эмоция
                    reaction = message_data['text'][entity.offset:entity.offset + entity.length]
                    
                    # Получаем количество очков за эмоцию
                    points = await get_emotion_points(reaction, chat_id)
                    
                    if points:
                        # Получаем текущие очки пользователя
                        current_points = await get_user_points(user_id, chat_id)
                        new_points = current_points + points
                        
                        # Обновляем очки пользователя в базе
                        await set_user_points(user_id, chat_id, new_points)
                        
                        # Отправляем пользователю сообщение о начисленных очках
                        await bot.send_message(chat_id, f"Вы получили {points} очков за реакцию '{reaction}'!")
                    else:
                        # Если эмоция не настроена для начисления очков
                        await bot.send_message(chat_id, "Эта реакция не настроена для начисления очков.")
    
    return {"status": "ok"}
