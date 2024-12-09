# handlers/user_handlers.py

from aiogram import types
from database.queries import get_user_info, get_all_ranks, set_user_rank, set_user_points, get_initial_rank
from database.users import add_user
from database.connection import db
import logging


# Функция для получения user_id по username
async def get_user_id_by_username(username: str, chat_id: int):
    query = "SELECT user_id FROM users WHERE username = %s AND chat_id = %s"
    result = await db.fetchone(query, (username, chat_id))
    return result['user_id'] if result else None


# Функция для получения информации о пользователе по user_id или username
async def get_user_info_handler(message: types.Message):
    chat_id = message.chat.id
    
    # Если аргумент передан (можно использовать либо user_id, либо username)
    try:
        if message.text.split()[1].isdigit():  # Если это user_id
            user_id = int(message.text.split()[1])
            user_info = await get_user_info(user_id, chat_id)
        else:  # Иначе это username
            username = message.text.split()[1]
            user_id = await get_user_id_by_username(username, chat_id)
            if user_id:
                user_info = await get_user_info(user_id, chat_id)
            else:
                await message.reply(f"Пользователь с username @{username} не найден.")
                return

        if user_info:
            # Используем имена колонок для получения данных
            rank = user_info['rank']
            points = user_info['points']
            await message.reply(f"Информация о пользователе {user_info['user_id']}: Ранг - {rank}, Очки - {points}")
        else:
            await message.reply("Пользователь не найден в базе данных.")
    except IndexError:
        await message.reply("Пожалуйста, укажите user_id или username.")
    except Exception as e:
        logging.error(f"Ошибка при получении информации о пользователе: {e}")
        await message.reply("Произошла ошибка при обработке запроса.")


# ДОРРАБОТАТЬ ЭТОТ ММОЕНТ С РЕГИСТАРРЦИЕЙ ЧАТА 
# Добавляем пользователя в базу данных с учетом chat_id и username
# Добавляем пользователя в базу данных с учетом chat_id
# Обработчик для команды /start (или при добавлении нового пользователя)
async def add_user_handler(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    username = message.from_user.username  # Получаем username пользователя
    rank = ""  # Изначально пустой ранг
    points = 0

    # Логируем информацию для отладки
    logging.info(f"Received user info: user_id={user_id}, chat_id={chat_id}, username={username}")

    # Проверка, существует ли чат в таблице
    chat_check_query = "SELECT chat_id FROM chats WHERE chat_id = %s"
    chat_exists = await db.fetchval(chat_check_query, (chat_id,))

    if not chat_exists:
        # Если чата нет в базе, проверяем, является ли это личным чатом
        if message.chat.type == "private":
            chat_name = "Личный чат"  # Название для личных чатов
        else:
            chat_name = message.chat.title if message.chat.title else "Неизвестное название чата"

        # Логируем информацию о добавлении чата
        logging.info(f"Chat does not exist, adding chat: chat_id={chat_id}, chat_name={chat_name}")

        # Добавляем чат в базу данных
        insert_chat_query = "INSERT INTO chats (chat_id, chat_name) VALUES (%s, %s)"
        await db.execute(insert_chat_query, (chat_id, chat_name))

    # Добавляем пользователя в базу данных
    try:
        # Добавляем пользователя с пустым рангом
        await add_user(user_id, chat_id, username, rank, points)
        await message.reply("Вы были успешно добавлены в систему!")

        # Получаем начальный ранг для этого чата
        initial_rank = await get_initial_rank(chat_id)
        if initial_rank:
            # Устанавливаем начальный ранг
            await set_user_rank(user_id, chat_id, initial_rank)
            await message.reply(f"Ваш начальный ранг установлен как {initial_rank}.")

        logging.info(f"User {user_id} successfully added to the system in chat {chat_id}")
    except Exception as e:
        logging.error(f"Error adding user {user_id} to chat {chat_id}: {e}")
        await message.reply("Произошла ошибка при добавлении пользователя в систему.")





async def update_user_rank_based_on_points(user_id: int, chat_id: int, points: int):
    # Получаем все ранги для конкретного чата
    ranks = await get_all_ranks(chat_id)
    if not ranks:
        logging.error(f"Не удалось найти ранги для чата {chat_id}.")
        return  # Если нет рангов, ничего не делаем

    logging.info(f"Доступные ранги для чата {chat_id}: {ranks}")

    # Преобразуем очки и требуемые баллы в int для безопасного сравнения
    points = int(points)

    # Сортируем ранги по требуемым баллам в убывающем порядке
    ranks = sorted(ranks, key=lambda r: r['points_required'], reverse=True)

    # Ищем соответствующий ранг
    new_rank = None  # Начальный ранг по умолчанию
    logging.info(f"Начинаем обновление ранга для пользователя {user_id} с очками {points}.")

    for rank in ranks:
        rank_name = rank['rank_name']
        required_points = int(rank['points_required'])  # Преобразуем требуемые баллы в int
        logging.info(f"Проверка: {rank_name} с требуемыми баллами {required_points}. Текущие очки пользователя: {points}.")

        if points >= required_points:
            new_rank = rank_name  # Обновляем ранг, если количество очков больше или равно необходимым
            break  # Прерываем, как только находим первый подходящий ранг

    # Если новый ранг не найден, устанавливаем начальный ранг для этого чата
    if new_rank is None:
        initial_rank = await get_initial_rank(chat_id)  # Получаем начальный ранг для чата
        new_rank = initial_rank if initial_rank else "Новичок"  # Если нет начального ранга, назначаем "Новичок"
    
    # Получаем текущий ранг пользователя
    current_user_info = await get_user_info(user_id, chat_id)
    current_rank = current_user_info['rank']
    logging.info(f"Текущий ранг пользователя {user_id}: {current_rank}. Новый ранг: {new_rank}.")

    # Если ранг изменился, обновляем его в базе данных
    if current_rank != new_rank:
        await set_user_rank(user_id, chat_id, new_rank)
        logging.info(f"Ранг пользователя {user_id} обновлен на {new_rank}.")
    else:
        logging.info(f"Ранг пользователя {user_id} не изменился.")

