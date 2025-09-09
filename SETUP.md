# Настройка DNM Dashboard с PostgreSQL

## Установка зависимостей

1. Установите необходимые пакеты:
```bash
pip install -r requirements.txt
```

## Настройка базы данных

1. Создайте файл `.env` в корне проекта со следующим содержимым:
```env
# Database Configuration (с префиксом DB_)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dnm_dashboard
DB_USER=postgres
DB_PASSWORD=your_password_here

# Application Configuration
DEBUG=False
HOST=127.0.0.1
PORT=8050
```

2. Замените значения на ваши реальные настройки PostgreSQL:
   - `DB_HOST` - хост базы данных
   - `DB_PORT` - порт базы данных (по умолчанию 5432)
   - `DB_NAME` - имя базы данных
   - `DB_USER` - имя пользователя
   - `DB_PASSWORD` - пароль пользователя

## Преимущества Pydantic Settings

Конфигурация теперь использует Pydantic V2 Settings, что обеспечивает:
- ✅ Автоматическую валидацию типов данных
- ✅ Поддержку переменных окружения с префиксами
- ✅ Автоматическое чтение из .env файла
- ✅ Подробные описания полей
- ✅ Безопасность типов (type safety)
- ✅ Игнорирование лишних переменных окружения (extra='ignore')

## Тестирование конфигурации

Для проверки настроек используйте:
```bash
python test_config.py
```

## Структура базы данных

Убедитесь, что в вашей базе данных PostgreSQL есть следующие таблицы:
- `public.dnm_ro_data` - данные о заказ-нарядах
- `public.sales` - данные о продажах
- `public.vin_model` - соответствие VIN кодов и моделей

## Запуск приложения

```bash
python app/dnm.py
```

Приложение будет доступно по адресу: http://127.0.0.1:8050

## Fallback режим

Если подключение к базе данных не удается, приложение автоматически переключится на использование CSV файла `data/aug_25.csv`.

## Тестирование подключения

Для тестирования подключения к базе данных можно использовать функцию:
```python
from database.queries import test_database_connection
print(test_database_connection())
```
