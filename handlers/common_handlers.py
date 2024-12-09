# handlers/common_handlers.py

from aiogram import types

async def help_handler(message: types.Message):
    help_text = (
        "Привет! Я — бот, который поможет управлять рангами и очками пользователей.\n\n"
        "Доступные команды:\n\n"
        
        # Команды для пользователей
        "**Для пользователей:**\n"
        "/start - Зарегистрироваться в системе\n"
        "/get_user_info - Получить информацию о себе\n\n"
        
        # Команды для администраторов
        "**Для администраторов:**\n"
        "/set_initial_rank <rank> - Установить начальный ранг для новых пользователей\n"
        "/add_rank <rank_name> <points> - Добавить новый ранг с требованиями по очкам\n"
        "/remove_rank <rank_name> - Удалить ранг\n"
        "/list_ranks - Список всех рангов\n"
        "/set_emotion <emotion> <points> - Установить очки за эмоцию\n"
        "/remove_emotion <emotion> - Удалить эмоцию\n"
        "/list_emotions - Список всех эмоций\n"
        "/set_user_rank <user_id> <rank> - Установить ранг пользователю\n"
        "/set_user_points <user_id> <points> - Установить очки пользователю\n"
        "/reset_user <user_id> - Сбросить данные пользователя\n"
        "/list_users - Список всех пользователей\n"
        "/get_settings - Получить текущие настройки\n"
        "/reset_all - Сбросить все данные\n\n"
        
        "Если вам нужно что-то другое, напишите, и я помогу!"
    )
    await message.reply(help_text)
