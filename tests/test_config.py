#!/usr/bin/env python3
"""
Скрипт для тестирования конфигурации Pydantic Settings
"""

from config import settings


def main():
    """Тестирование настроек"""
    print('=== Тест конфигурации Pydantic Settings ===\n')

    # Тест настроек базы данных
    print('📊 Настройки базы данных:')
    print(f'  Host: {settings.database.host}')
    print(f'  Port: {settings.database.port}')
    print(f'  Database: {settings.database.name}')
    print(f'  User: {settings.database.user}')
    print(f'  Password: {"*" * len(settings.database.password)}')

    # Тест параметров подключения
    print('\n🔗 Параметры подключения:')
    conn_params = settings.database.connection_params
    for key, value in conn_params.items():
        if key == 'password':
            value = '*' * len(value)
        print(f'  {key}: {value}')

    # Тест настроек приложения
    print('\n🚀 Настройки приложения:')
    print(f'  Debug: {settings.app.debug}')
    print(f'  Host: {settings.app.host}')
    print(f'  Port: {settings.app.port}')

    # Тест обратной совместимости
    print('\n🔄 Обратная совместимость:')
    from config import DB_CONFIG, APP_CONFIG
    print(f'  DB_CONFIG: {DB_CONFIG}')
    print(f'  APP_CONFIG: {APP_CONFIG}')

    print('\n✅ Все тесты пройдены успешно!')


if __name__ == '__main__':
    main()
