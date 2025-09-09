from contextlib import contextmanager

import pandas as pd
import psycopg2

from config import settings


class DatabaseConnection:
    """Класс для работы с PostgreSQL базой данных"""

    def __init__(self):
        self.config = settings.database.connection_params

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для подключения к базе данных"""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Выполняет SQL запрос и возвращает результат в виде DataFrame

        Args:
            query (str): SQL запрос
            params (dict): Параметры для запроса

        Returns:
            pd.DataFrame: Результат запроса
        """
        with self.get_connection() as conn:
            try:
                df = pd.read_sql_query(query, conn, params=params)
                return df
            except Exception as e:
                print(f'Ошибка при выполнении запроса: {e}')
                raise e

    def test_connection(self) -> bool:
        """
        Проверяет подключение к базе данных

        Returns:
            bool: True если подключение успешно, False в противном случае
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                return True
        except Exception as e:
            print(f'Ошибка подключения к базе данных: {e}')
            return False


# Создаем глобальный экземпляр для использования в приложении
db_connection = DatabaseConnection()
