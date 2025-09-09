from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Настройки базы данных PostgreSQL"""

    host: str = Field(
        default='localhost',
        description='Хост базы данных'
        )
    port: int = Field(
        default=5432,
        description='Порт базы данных'
        )
    name: str = Field(
        default='dnm_dashboard',
        description='Имя базы данных'
    )
    user: str = Field(
        default='postgres',
        description='Пользователь базы данных'
    )
    password: str = Field(
        default='',
        description='Пароль базы данных'
        )

    model_config = SettingsConfigDict(
        env_prefix='DB_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    @property
    def connection_params(self) -> dict:
        """Возвращает параметры подключения для psycopg2"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.name,
            'user': self.user,
            'password': self.password,
        }

    @property
    def sqlalchemy_url(self) -> str:
        """Возвращает URL для подключения через SQLAlchemy"""
        return (f'postgresql://{self.user}:{self.password}@'
                f'{self.host}:{self.port}/{self.name}')


class AppSettings(BaseSettings):
    """Настройки приложения"""

    debug: bool = Field(
        default=False,
        description='Режим отладки'
        )
    host: str = Field(
        default='127.0.0.1',
        description='Хост приложения'
        )
    port: int = Field(
        default=8050,
        description='Порт приложения'
        )

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Игнорируем лишние переменные окружения
    )


class Settings(BaseSettings):
    """Основные настройки приложения"""

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    app: AppSettings = Field(default_factory=AppSettings)

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'  # Игнорируем лишние переменные окружения
    )


# Создаем глобальный экземпляр настроек
settings = Settings()

# Для обратной совместимости
DB_CONFIG = settings.database.connection_params
APP_CONFIG = {
    'debug': settings.app.debug,
    'host': settings.app.host,
    'port': settings.app.port,
}
