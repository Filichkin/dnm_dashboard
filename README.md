# DNM RO Dashboard

Интерактивный дашборд для анализа данных по заказ-нарядам (RO) по моделям автомобилей.

## Описание

Дашборд предоставляет визуализацию ключевых метрик по моделям автомобилей:
- Топ-10 моделей по общей прибыли
- Топ-10 моделей по нормо-часам
- Средние показатели по моделям
- Анализ заказ-нарядов по возрастным группам
- Интерактивная таблица с детальными данными

![DNM Dashboard Preview](example.png)

*Пример интерфейса дашборда*

## Функциональность

### Графики
1. **Топ-10 по общей прибыли** - модели с наибольшим `total_ro_cost`
2. **Топ-10 по общим нормо-часам** - модели с наибольшим `labor_hours_0_10`
3. **Топ-10 по средним нормо-часам на автомобиль** - `aver_labor_hours_per_vhc`
4. **Топ-10 по среднему чеку** - `avg_ro_cost`
5. **Топ-10 по соотношению RO/UIO** - `ro_ratio_of_uio_10y`
6. **Количество заказ-нарядов по возрастным группам** - анализ по годам (0-3, 4-5, 6-10)

### Таблица данных
- Отсортирована по `total_ro_cost` по убыванию
- Исключены строки с нулевым `total_0_10`
- Приоритетный порядок столбцов
- Форматирование чисел с разделителями тысяч

## Установка

### Требования
- Python 3.8+
- pip

### Шаги установки

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd dnm_dashboard
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Для создания PDF-отчётов (опционально):**
   ```bash
   pip install selenium
   ```

## Использование

### Запуск дашборда

1. **Активируйте виртуальное окружение:**
   ```bash
   source venv/bin/activate  # Linux/Mac
   # или
   venv\Scripts\activate     # Windows
   ```

2. **Запустите дашборд:**
   ```bash
   python dnm.py
   ```

3. **Откройте браузер:**
   Перейдите по адресу: `http://127.0.0.1:8050/`

### Создание PDF-отчётов

#### Метод 1: Обычный PDF (отдельные страницы)
```bash
python save_dash.py
```
Создаёт `dnm_dashboard.pdf` с каждым графиком на отдельной странице.

#### Метод 2: Одностраничный PDF (скриншот браузера)
```bash
python save_dash.py
```
Создаёт `dnm_dashboard_single.pdf` с точным отображением дашборда.

**Примечание:** Для метода 2 требуется установленный Selenium и Chrome/ChromeDriver.

## Структура данных

### Входной файл: `data.csv`

Структура данных включает следующие ключевые поля:

| Поле | Описание |
|------|----------|
| `model` | Модель автомобиля |
| `uio_10y` | Количество автомобилей в возрасте до 10 лет |
| `total_0_10` | Общее количество заказ-нарядов |
| `total_ro_cost` | Общая стоимость заказ-нарядов |
| `avg_ro_cost` | Средний чек заказ-наряда |
| `labor_hours_0_10` | Общие нормо-часы |
| `aver_labor_hours_per_vhc` | Средние нормо-часы на автомобиль |
| `ro_ratio_of_uio_10y` | Соотношение RO к UIO |

### Возрастные группы
- `age_0_3` - автомобили 0-3 лет
- `age_4_5` - автомобили 4-5 лет  
- `age_6_10` - автомобили 6-10 лет

## Настройка

### Изменение цветовой схемы
В файле `dnm.py` можно изменить палитру цветов:
```python
gray_blue_colors = [
    '#90a4ae',  # blue gray (calm)
    '#a5d6a7',  # soft green
    # ... другие цвета
]
```

### Настройка размера графиков
```python
GRAPH_HEIGHT = 350  # Высота графиков в пикселях
```

### Фильтрация данных
В таблице автоматически исключаются строки с `total_0_10 == 0`.

## Зависимости

### Основные
- `dash` - веб-фреймворк для дашбордов
- `pandas` - обработка данных
- `plotly` - создание интерактивных графиков
- `matplotlib` - создание статических графиков
- `reportlab` - генерация PDF

### Дополнительные (для PDF)
- `selenium` - автоматизация браузера для скриншотов

## Структура проекта

```
dnm_dashboard/
├── dnm.py              # Основной файл дашборда
├── save_dash.py        # Скрипт для создания PDF
├── data.csv            # Входные данные
├── requirements.txt    # Зависимости
├── README.md          # Документация
└── venv/              # Виртуальное окружение
```

## Возможные проблемы

### Ошибка подключения к дашборду
Если получаете `ERR_CONNECTION_REFUSED` при создании PDF:
1. Убедитесь, что дашборд запущен
2. Проверьте, что порт 8050 свободен
3. Используйте обычный метод PDF

### Проблемы с Selenium
Если возникают проблемы с автоматическими скриншотами:
1. Установите ChromeDriver
2. Обновите Selenium: `pip install --upgrade selenium`
3. Используйте обычный метод PDF

## Лицензия

MIT License

Copyright (c) 2025 DNM Dashboard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Поддержка

При возникновении проблем создайте issue в репозитории или обратитесь к разработчику.
