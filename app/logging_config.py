"""
Конфигурация логирования для DNM Dashboard
"""
import sys
from pathlib import Path
from loguru import logger


# Удаляем стандартный обработчик loguru
logger.remove()

# Настройка логирования


def setup_logging():
    """
    Настраивает логирование для приложения
    """
    # Создаем директорию для логов
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Формат логов
    log_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
        '<level>{level: <8}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
        '<level>{message}</level>'
    )

    # Логирование в консоль
    logger.add(
        sys.stdout,
        format=log_format,
        level='INFO',
        colorize=True,
        backtrace=True,
        diagnose=True
    )

    # Логирование в файл (общие логи)
    logger.add(
        log_dir / 'app.log',
        format=log_format,
        level='DEBUG',
        rotation='10 MB',
        retention='30 days',
        compression='zip',
        backtrace=True,
        diagnose=True
    )

    # Логирование SQL запросов в отдельный файл
    logger.add(
        log_dir / 'sql_queries.log',
        format=log_format,
        level='DEBUG',
        rotation='5 MB',
        retention='7 days',
        compression='zip',
        filter=lambda record: (
            'SQL' in record['message'] or
            'запрос' in record['message'].lower()
        )
    )

    # Логирование ошибок в отдельный файл
    logger.add(
        log_dir / 'errors.log',
        format=log_format,
        level='ERROR',
        rotation='1 MB',
        retention='90 days',
        compression='zip',
        backtrace=True,
        diagnose=True
    )

    logger.info('Логирование настроено успешно')


# Инициализация логирования при импорте модуля
setup_logging()
