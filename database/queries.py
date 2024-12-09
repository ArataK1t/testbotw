#queries.py
from database.connection import Database
import logging
# Создаём объект db для работы с базой данных
db = Database()

# Установить начальный ранг для чата
async def set_initial_rank(chat_id: int, rank: str):
    query = """
    INSERT INTO settings (chat_id, initial_rank)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE initial_rank = %s
    """
    await db.execute(query, (chat_id, rank, rank))
    logging.info(f"Начальный ранг для чата {chat_id} установлен на {rank}.")


# Функция для получения начального ранга чата
async def get_initial_rank(chat_id: int):
    query = "SELECT initial_rank FROM settings WHERE chat_id = %s"
    result = await db.fetchone(query, (chat_id,))
    return result['initial_rank'] if result else None


# Установить требования к рангу для конкретного чата
async def set_rank_requirements(rank_name: str, chat_id: int, points_required: int):
    query = """
    INSERT INTO ranks (rank_name, chat_id, points_required)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE points_required = %s
    """
    await db.execute(query, (rank_name, chat_id, points_required, points_required))


# Установить эмоцию и её очки
async def set_emotion_reward(chat_id: int, emotion: str, points: int):
    query = """
    INSERT INTO emotions (chat_id, emotion, points)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE points = %s
    """
    await db.execute(query, (chat_id, emotion, points, points))


async def set_user_rank(user_id: int, chat_id: int, rank: str):
    query = "UPDATE users SET `rank` = %s WHERE user_id = %s AND chat_id = %s"
    try:
        result = await db.execute(query, (rank, user_id, chat_id))
        if result:
            logging.info(f"Ранг для пользователя user_id={user_id} в чате {chat_id} успешно обновлен на {rank}.")
        else:
            logging.error(f"Не удалось обновить ранг для пользователя user_id={user_id} в чате {chat_id}.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении ранга для пользователя user_id={user_id} в чате {chat_id}: {e}")




# Установить очки пользователя
async def set_user_points(user_id: int, chat_id: int, points: int):
    query = "UPDATE users SET points = %s WHERE user_id = %s AND chat_id = %s"
    await db.execute(query, (points, user_id, chat_id))

# Сбросить данные пользователя
async def reset_user(user_id: int, chat_id: int):
    query = "UPDATE users SET rank = 'Новичек', points = 0 WHERE user_id = %s AND chat_id = %s"
    await db.execute(query, (user_id, chat_id))

# Получить все эмоции
async def get_all_emotions(chat_id: int):
    query = "SELECT emotion, points FROM emotions WHERE chat_id = %s"
    return await db.fetchall(query, (chat_id,))

# Получение очков за конкретную эмоцию
async def get_emotion_points(emotion: str, chat_id: int):
    query = "SELECT points FROM emotions WHERE chat_id = %s AND emotion = %s"
    result = await db.fetchone(query, (chat_id, emotion))
    return result['points'] if result else None


# Получить все ранги
# Получить все ранги для конкретного чата
async def get_all_ranks(chat_id: int):
    query = "SELECT * FROM ranks WHERE chat_id = %s"
    try:
        result = await db.fetchall(query, (chat_id,))
        if result:
            return result
        else:
            logging.error(f"Для chat_id={chat_id} не найдены ранги.")
            return []
    except Exception as e:
        logging.error(f"Ошибка при получении рангов для chat_id={chat_id}: {e}")
        return []



async def get_user_info(user_id: int, chat_id: int):
    query = "SELECT user_id, chat_id, username, `rank`, points FROM users WHERE user_id = %s AND chat_id = %s"
    try:
        result = await db.fetchone(query, (user_id, chat_id))
        if result:
            return result
        else:
            logging.error(f"Пользователь с user_id={user_id} и chat_id={chat_id} не найден.")
            return None
    except Exception as e:
        logging.error(f"Ошибка при получении информации о пользователе: {e}")
        return None

async def get_user_points(user_id: int, chat_id: int) -> int:
    """
    Получает количество очков пользователя в чате.
    """
    query = "SELECT points FROM users WHERE user_id = %s AND chat_id = %s"
    result = await db.fetchone(query, (user_id, chat_id))
    if result:
        return result['points']  # Предполагается, что результат возвращается как словарь
    return 0  # Если пользователя нет в базе, возвращаем 0 очков


# Получить список всех пользователей
async def get_all_users(chat_id: int):
    query = "SELECT * FROM users WHERE chat_id = %s"
    return await db.fetchall(query, (chat_id,))

# Получить текущие настройки (например, начальный ранг)
async def get_current_settings():
    query = "SELECT * FROM settings LIMIT 1"
    result = await db.fetchone(query)
    if result:
        return {"initial_rank": result[1]}  # Возвращаем только начальный ранг
    return {"initial_rank": "Новичек"}  # Если нет настроек, возвращаем дефолтный


# УДАЛЯЕМ РАНГ
async def remove_rank(rank_name: str, chat_id: int):
    # Удаляем ранг из таблицы ranks
    query = """
    DELETE FROM ranks
    WHERE rank_name = %s AND chat_id = %s
    """
    await db.execute(query, (rank_name, chat_id))

    # Получаем все доступные ранги для чата
    ranks = await get_all_ranks(chat_id)
    
    if not ranks:
        # Если нет доступных рангов, устанавливаем начальный ранг для всех пользователей
        logging.warning(f"Для чата {chat_id} не осталось доступных рангов.")
        initial_rank = await get_initial_rank(chat_id)
        if initial_rank:
            query = """
            UPDATE users SET `rank` = %s WHERE chat_id = %s
            """
            await db.execute(query, (initial_rank, chat_id))
            logging.info(f"Все пользователи чата {chat_id} теперь имеют начальный ранг: {initial_rank}.")
        else:
            logging.warning(f"Не установлен начальный ранг для чата {chat_id}.")
        return

    # Сортируем ранги по очкам, от наибольшего к наименьшему
    ranks = sorted(ranks, key=lambda r: r['points_required'], reverse=True)

    # Получаем всех пользователей, у которых был удалённый ранг
    query = """
    SELECT user_id, points FROM users
    WHERE `rank` = %s AND chat_id = %s
    """
    users_with_rank = await db.fetchall(query, (rank_name, chat_id))

    # Пересчитываем ранг для каждого пользователя
    for user in users_with_rank:
        user_id = user['user_id']
        points = user['points']

        # Ищем новый ранг, который подходит пользователю по очкам
        new_rank = None
        for rank in ranks:
            if points >= rank['points_required']:
                new_rank = rank['rank_name']
                break

        if new_rank:
            # Устанавливаем новый ранг пользователю
            await set_user_rank(user_id, chat_id, new_rank)
            logging.info(f"Пользователю {user_id} в чате {chat_id} установлен новый ранг: {new_rank}.")
        else:
            # Если не нашли подходящий ранг, можно установить начальный (если есть)
            initial_rank = await get_initial_rank(chat_id)
            if initial_rank:
                await set_user_rank(user_id, chat_id, initial_rank)
                logging.info(f"Пользователю {user_id} в чате {chat_id} установлен начальный ранг: {initial_rank}.")


# Удалить эмоцию
async def remove_emotion(chat_id: int, emotion: str):
    query = "DELETE FROM emotions WHERE chat_id = %s AND emotion = %s"
    await db.execute(query, (chat_id, emotion))


# Сбросить все данные (все пользователи, эмоции, ранги и т.д.)
async def reset_all_data():
    # Сбросить всех пользователей
    await db.execute("UPDATE users SET `rank` = 'Новичек', points = 0")
    
    # Удалить все эмоции
    await db.execute("DELETE FROM emotions")
    
    # Удалить все ранги
    await db.execute("DELETE FROM ranks")
    
    # Сбросить настройки
    await db.execute("DELETE FROM settings")

    # Вставить начальный ранг, если он был задан ранее
    await db.execute("INSERT INTO settings (initial_rank) VALUES ('Новичек') ON DUPLICATE KEY UPDATE initial_rank = 'Новичек'")
