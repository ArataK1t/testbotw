# handlers/creator_handlers.py
import logging
from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import CallbackQuery
from handlers.user_handlers import get_user_id_by_username, update_user_rank_based_on_points
from database.queries import (set_user_rank, set_user_points, reset_user, 
                              set_initial_rank, set_rank_requirements, 
                              set_emotion_reward, get_all_emotions, 
                              get_all_ranks, get_user_info, get_all_users, 
                              remove_rank, remove_emotion, get_current_settings,
                              reset_all_data, get_emotion_points, get_user_points)
from config import CREATOR_ID


async def is_creator(user_id: int):
    return user_id == CREATOR_ID



# Команда: Установить начальный ранг для новых пользователей
async def set_initial_rank_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        rank = message.text.split(' ', 1)[1].strip()
        chat_id = message.chat.id
        await set_initial_rank(chat_id, rank)
        await message.reply(f"Начальный ранг для новых пользователей в этом чате установлен на {rank}.")
    except IndexError:
        await message.reply("Пожалуйста, укажите имя ранга.")


# Команда: Добавить новый ранг
async def add_rank_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        args = message.text.split(' ', 2)
        rank_name = args[1]
        chat_id = message.chat.id
        points_required = int(args[2])
        await set_rank_requirements(rank_name, chat_id, points_required)
        await message.reply(f"Ранг {rank_name} с требованиями {points_required} очков добавлен.")
    except (IndexError, ValueError):
        await message.reply("Неверный формат. Используйте команду: /add_rank <название_ранга> <количество_очков>.")


# Команда: Удалить ранг
async def remove_rank_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        rank_name = message.text.split(' ', 1)[1].strip()
        chat_id = message.chat.id  # Получаем chat_id из сообщения
        await remove_rank(rank_name, chat_id)  # Передаем chat_id в функцию
        await message.reply(f"Ранг {rank_name} удален.")
    except IndexError:
        await message.reply("Пожалуйста, укажите название ранга для удаления.")



# Команда: Просмотр всех рангов
async def list_ranks_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    chat_id = message.chat.id  # Получаем chat_id

    ranks = await get_all_ranks(chat_id)  # Передаем chat_id в запрос
    if ranks:
        response = "Список всех рангов:\n"
        for rank in ranks:
            response += f"{rank['rank_name']}: {rank['points_required']} очков\n"  # Используем ключи словаря для получения данных
        await message.reply(response)
    else:
        await message.reply("Ранги не настроены.")



# Команда: Установить очки за эмоцию
async def set_emotion_reward_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        args = message.text.split(' ', 2)
        emotion = args[1]
        points = int(args[2])
        chat_id = message.chat.id

        await set_emotion_reward(chat_id, emotion, points)
        await message.reply(f"Эмоция {emotion} теперь дает {points} очков.")
    except (IndexError, ValueError):
        await message.reply("Неверный формат. Используйте команду: /set_emotion <эмоция> <очки>.")


# Команда: Удалить эмоцию
async def remove_emotion_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        emotion = message.text.split(' ', 1)[1].strip()
        chat_id = message.chat.id

        await remove_emotion(chat_id, emotion)
        await message.reply(f"Эмоция {emotion} удалена.")
    except IndexError:
        await message.reply("Пожалуйста, укажите эмоцию для удаления.")


# Команда: Просмотр всех эмоций
async def list_emotions_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    chat_id = message.chat.id
    emotions = await get_all_emotions(chat_id)

    if emotions:
        response = "Список всех эмоций:\n"
        for emotion, points in emotions:
            response += f"{emotion}: {points} очков\n"
        await message.reply(response)
    else:
        await message.reply("Эмоции не настроены.")

# Обработчик реакции (эмодзи), который будет вызван при реакции на сообщение
async def handle_reaction(callback_query: types.CallbackQuery):
    """
    Обрабатывает реакцию (эмодзи), добавленную к сообщению.
    """
    try:
        reacting_user_id = callback_query.from_user.id  # ID пользователя, который поставил реакцию
        message_user_id = callback_query.message.from_user.id  # ID пользователя, на чье сообщение поставлена реакция
        chat_id = callback_query.message.chat.id  # ID чата, в котором была реакция
        emotion = callback_query.data.split('_')[1]  # Извлекаем эмоцию (смайл) из данных callback

        # Получаем количество очков за эту эмоцию
        points = await get_emotion_points(emotion, chat_id)
        if points:
            # Получаем текущие очки пользователя (на чье сообщение поставлена реакция)
            current_points = await get_user_points(message_user_id, chat_id)
            new_points = current_points + points

            # Обновляем очки пользователя
            await set_user_points(message_user_id, chat_id, new_points)

            # Отправляем сообщение в чат
            await callback_query.message.reply(f"Вы получили {points} очков за реакцию '{emotion}' на ваше сообщение.")
        else:
            # Если эмоция не настроена для начисления очков
            await callback_query.message.reply("Эта реакция не настроена для начисления очков.")
    except Exception as e:
        # Логируем ошибку, если она произошла
        logging.error(f"Ошибка при обработке реакции: {e}")






async def set_user_rank_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        args = message.text.split(' ', 2)
        if len(args) < 3:
            await message.reply("Неверный формат. Используйте команду: /set_user_rank <user_id/username> <rank_name>.")
            return

        identifier = args[1].strip()  # Это может быть либо user_id, либо username
        rank = args[2]
        chat_id = message.chat.id

        logging.info(f"Попытка установить ранг {rank} для пользователя с identifier={identifier} в чате {chat_id}.")

        # Проверяем, является ли это user_id или username
        if identifier.isdigit():  # Если это число, значит это user_id
            user_id = int(identifier)
        else:  # Иначе ищем по username
            user_id = await get_user_id_by_username(identifier, chat_id)
            if not user_id:
                await message.reply(f"Пользователь с username {identifier} не найден.")
                return

        # Устанавливаем новый ранг
        await set_user_rank(user_id, chat_id, rank)
        
        # Получаем текущие очки пользователя
        user_info = await get_user_info(user_id, chat_id)
        if user_info:
            points = user_info['points']
            # Обновляем ранг, если нужно
            await update_user_rank_based_on_points(user_id, chat_id, points)

            await message.reply(f"Ранг пользователя {user_id} в чате {chat_id} установлен на {rank}.")
        else:
            await message.reply("Не удалось найти информацию о пользователе.")

    except Exception as e:
        logging.error(f"Ошибка при обработке команды set_user_rank_handler: {e}")
        await message.reply("Произошла ошибка при обработке команды.")





# Команда: Установить очки для пользователя 
async def set_user_points_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        args = message.text.split(' ', 2)

        # Проверяем количество аргументов
        if len(args) != 3:
            await message.reply("Неверный формат. Используйте команду: /set_user_points <user_id/username> <points>.")
            return

        identifier = args[1].strip()  # Это может быть либо user_id, либо username
        points = int(args[2])  # Преобразуем очки в целое число
        chat_id = message.chat.id

        # Проверка, является ли это user_id или username
        if identifier.isdigit():  # Если это число, значит это user_id
            user_id = int(identifier)
        else:  # Иначе ищем по username
            user_id = await get_user_id_by_username(identifier, chat_id)
            if not user_id:
                await message.reply(f"Пользователь с username {identifier} не найден.")
                return

        # Обновляем очки пользователя
        await set_user_points(user_id, chat_id, points)

        # Обновляем ранг пользователя в зависимости от очков
        await update_user_rank_based_on_points(user_id, chat_id, points)

        # Отправляем один ответ пользователю
        await message.reply(f"Очки пользователя {user_id} в чате {chat_id} обновлены до {points}. Ранг пользователя был обновлен.")

    except (IndexError, ValueError):
        await message.reply("Неверный формат. Используйте команду: /set_user_points <user_id/username> <points>.")



# Команда: Сбросить данные пользователя
async def reset_user_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    try:
        identifier = message.text.split(' ', 1)[1].strip()  # Это может быть либо user_id, либо username
        chat_id = message.chat.id

        # Проверяем, является ли это user_id или username
        if identifier.isdigit():  # Если это число, значит это user_id
            user_id = int(identifier)
        else:  # Иначе ищем по username
            user_id = await get_user_id_by_username(identifier, chat_id)
            if not user_id:
                await message.reply(f"Пользователь с username {identifier} не найден.")
                return

        await reset_user(user_id, chat_id)
        await message.reply(f"Данные пользователя {user_id} в чате {chat_id} успешно сброшены.")
    except IndexError:
        await message.reply("Пожалуйста, укажите user_id или username пользователя для сброса.")
    except ValueError:
        await message.reply("Неверный формат user_id.")



# Команда: Просмотр всех пользователей (с возможностью поиска по username или user_id)
async def list_users_handler(message: types.Message):
    # Проверка, является ли пользователь создателем
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    chat_id = message.chat.id  # Получаем chat_id

    # Если в сообщении есть дополнительные аргументы
    if len(message.text.split()) > 1:
        identifier = message.text.split(' ', 1)[1].strip()  # Это может быть либо user_id, либо username

        # Проверяем, является ли это user_id или username
        if identifier.isdigit():  # Если это число, значит это user_id
            user_id = int(identifier)
            users = await get_user_info(user_id, chat_id)  # Передаем chat_id в функцию
            if users:
                response = f"Пользователь найден:\nID: {users['user_id']}, Ник: {users['username']}, Ранг: {users['rank']}, Очки: {users['points']}\n"
            else:
                response = "Пользователь не найден."
        else:  # Ищем по username
            user_id = await get_user_id_by_username(identifier, chat_id)  # Передаем chat_id в функцию
            if user_id:
                users = await get_user_info(user_id, chat_id)  # Передаем chat_id в функцию
                if users:
                    response = f"Пользователь найден:\nID: {users['user_id']}, Ник: {users['username']}, Ранг: {users['rank']}, Очки: {users['points']}\n"
                else:
                    response = "Пользователь не найден."
            else:
                response = f"Пользователь с username {identifier} не найден."
    else:
        # Если аргументов нет (то есть выводим всех пользователей)
        users = await get_all_users(chat_id)  # Передаем chat_id в функцию
        if users:
            response = "Список всех пользователей:\n"
            for user in users:
                # Убедитесь, что в данных есть поле 'username'
                response += f"ID: {user['user_id']}, Ник: {user.get('username', 'Не указан')}, Ранг: {user['rank']}, Очки: {user['points']}\n"
        else:
            response = "Пользователи не найдены."

    await message.reply(response)




# Команда: Просмотр текущих настроек
async def get_settings_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    settings = await get_current_settings()
    if settings:
        await message.reply(f"Текущие настройки:\nНачальный ранг: {settings['initial_rank']}")
    else:
        await message.reply("Настройки не установлены.")


# Команда: Сбросить все данные
async def reset_all_handler(message: types.Message):
    if not await is_creator(message.from_user.id):
        await message.reply("Эта команда доступна только создателю.")
        return

    # Здесь можно вызвать функцию для очистки всей информации в базе данных
    await reset_all_data()
    await message.reply("Все данные успешно сброшены.")
