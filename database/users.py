#users.py
from database.connection import Database
import logging

# Создаем объект db для работы с базой данных
db = Database()

# Добавление пользователя в таблицу users
async def add_user(user_id: int, chat_id: int, username: str = None, rank: str = "новичок", points: int = 0):
    query = """
    INSERT INTO users (user_id, chat_id, username, `rank`, points)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE username = %s, `rank` = %s, points = %s;
    """
    await db.execute(query, (user_id, chat_id, username, rank, points, username, rank, points))

# Получение информации о пользователе
async def get_user_info(user_id: int, chat_id: int):
    query = "SELECT user_id, chat_id, username, `rank`, points FROM users WHERE user_id = %s AND chat_id = %s"
    return await db.fetchone(query, (user_id, chat_id))

# Обновление ранга пользователя
async def set_user_rank(user_id: int, chat_id: int, rank: str):
    # Проверяем текущий ранг пользователя
    user_info = await get_user_info(user_id, chat_id)
    if user_info and user_info['rank'] == rank:
        logging.info(f"Ранг пользователя {user_id} в чате {chat_id} уже установлен на {rank}.")
        return  # Ранг не нужно обновлять

    query = "UPDATE users SET `rank` = %s WHERE user_id = %s AND chat_id = %s"
    try:
        result = await db.execute(query, (rank, user_id, chat_id))
        if result == 0:
            logging.error(f"Не удалось обновить ранг для пользователя {user_id} в чате {chat_id}.")
        else:
            logging.info(f"Ранг для пользователя {user_id} в чате {chat_id} успешно обновлен на {rank}.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении ранга для пользователя {user_id} в чате {chat_id}: {e}")



# Обновление очков пользователя
async def set_user_points(user_id: int, chat_id: int, points: int):
    query = "UPDATE users SET points = %s WHERE user_id = %s AND chat_id = %s"
    await db.execute(query, (points, user_id, chat_id))

# Сброс данных пользователя
async def reset_user(user_id: int, chat_id: int):
    # Сбрасываем ранг и очки, а не удаляем пользователя
    query = "UPDATE users SET `rank` = 'новичок', points = 0 WHERE user_id = %s AND chat_id = %s"
    await db.execute(query, (user_id, chat_id))

# Получение всех пользователей чата
async def get_all_users(chat_id: int):
    query = "SELECT user_id, chat_id, username, `rank`, points FROM users WHERE chat_id = %s"
    return await db.fetchall(query, (chat_id,))
