# database/connection.py
import logging
import aiomysql
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self):
        self.pool = None  # Инициализация пула соединений (пока не создан)

    async def init(self):
        """Инициализация пула соединений с базой данных MySQL."""
        if self.pool:
            logging.info("Database connection pool is already initialized")
            return

        try:
            logging.info("Initializing database connection pool...")
            self.pool = await aiomysql.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                db=DB_NAME,
                charset='utf8mb4',
                autocommit=True
            )
            logging.info("Database connection pool initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize the database connection pool: {e}")
            raise e

    async def execute(self, query, params=None):
        """Выполнение SQL-запроса без возвращаемого результата."""
        if not self.pool:
            await self.init()  # Инициализация пула, если он еще не создан

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params or ())
                    logging.info(f"Executed query: {query} with params: {params}")
        except Exception as e:
            logging.error(f"Error executing query: {query}. Error: {e}")
            raise e

    async def fetchone(self, query, params=None):
        """Получение одной строки из результата SQL-запроса."""
        if not self.pool:
            await self.init()  # Инициализация пула, если он еще не создан

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params or ())
                    result = await cursor.fetchone()
                    if result:
                        logging.info(f"Executed query: {query}, Fetched result: {result}")
                    else:
                        logging.info(f"Executed query: {query}, No result found.")
                    return result
        except Exception as e:
            logging.error(f"Error fetching data with query: {query}. Error: {e}")
            raise e

    async def fetchall(self, query, params=None):
        """Получение всех строк из результата SQL-запроса."""
        if not self.pool:
            await self.init()  # Инициализация пула, если он еще не создан

        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, params or ())
                    result = await cursor.fetchall()
                    logging.info(f"Executed query: {query}, Fetched results: {len(result)} rows.")
                    return result
        except Exception as e:
            logging.error(f"Error fetching data with query: {query}. Error: {e}")
            raise e

    async def close(self):
        """Закрытие пула соединений с базой данных."""
        if self.pool:
            self.pool.close()  # Закрываем пул
            await self.pool.wait_closed()  # Ждем завершения закрытия пула
            logging.info("Database connection pool closed.")
        else:
            logging.warning("Database pool is not initialized or already closed.")

    async def fetchval(self, query, params=None):
        """Получение одного значения из результата SQL-запроса."""
        try:
            result = await self.fetchone(query, params)
            if result is None:
                logging.info("No result found.")
                return None
            logging.info(f"Fetched value: {result.get('chat_id')}")
            return result.get('chat_id')  # Возвращаем нужное значение
        except Exception as e:
            logging.error(f"Error in fetchval with query: {query}. Error: {e}")
            raise e


# Создаем экземпляр класса Database для использования
db = Database()
