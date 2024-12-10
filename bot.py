#bot.py
import logging, requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils import executor
from config import BOT_TOKEN
from database.connection import Database  # Подключаем класс Database
from handlers.creator_handlers import (
    set_initial_rank_handler, add_rank_handler, remove_rank_handler, 
    list_ranks_handler, set_emotion_reward_handler, remove_emotion_handler, 
    list_emotions_handler, set_user_rank_handler, set_user_points_handler, 
    reset_user_handler, list_users_handler, get_settings_handler, reset_all_handler,
    handle_reaction
)
from handlers.user_handlers import get_user_info_handler, add_user_handler
from handlers.common_handlers import help_handler


logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Создаем экземпляр класса Database
db = Database()

# Подключаемся к базе данных перед запуском бота
async def on_startup(dp):
    await db.init()  # Инициализация подключения к базе данных

# Закрываем соединения с базой данных при завершении работы бота
async def on_shutdown(dp):
    await db.close()  # Закрываем подключение

# Регистрация хендлеров
def register_handlers(dp):
    # Хендлеры для создателя
    dp.register_message_handler(set_initial_rank_handler, commands=['set_initial_rank'])
    dp.register_message_handler(add_rank_handler, commands=['add_rank'])
    dp.register_message_handler(remove_rank_handler, commands=['remove_rank'])
    dp.register_message_handler(list_ranks_handler, commands=['list_ranks'])
    dp.register_message_handler(set_emotion_reward_handler, commands=['set_emotion'])
    dp.register_message_handler(remove_emotion_handler, commands=['remove_emotion'])
    dp.register_message_handler(list_emotions_handler, commands=['list_emotions'])
    dp.register_message_handler(set_user_rank_handler, commands=['set_user_rank'])
    dp.register_message_handler(set_user_points_handler, commands=['set_user_points'])
    dp.register_message_handler(reset_user_handler, commands=['reset_user'])
    dp.register_message_handler(list_users_handler, commands=['list_users'])
    dp.register_message_handler(get_settings_handler, commands=['get_settings'])
    dp.register_message_handler(reset_all_handler, commands=['reset_all'])
    
    dp.register_callback_query_handler(handle_reaction, lambda callback: callback.data.startswith('reaction_'))


# Хендлеры для пользователей
    dp.register_message_handler(get_user_info_handler, commands=['get_user_info'])
    dp.register_message_handler(add_user_handler, commands=['start'])

    # Общие хендлеры
    dp.register_message_handler(help_handler, commands=['help'])

# Обработчики команд



def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = "https://testbotw.ru/webhook/"
    
    response = requests.post(url, data={"url": webhook_url})
    
    if response.status_code == 200:
        print(f"Webhook set successfully to {webhook_url}")
    else:
        print(f"Failed to set webhook: {response.text}")









if __name__ == '__main__':
    register_handlers(dp)

    set_webhook()

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
