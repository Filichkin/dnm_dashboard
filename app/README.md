# DNM Dashboard — модули приложения

Дашборд переведён на дизайн-систему (dark + light) с темизацией через
CSS-переменные. Стили — library-native: один CSS-файл в `assets/`
плюс тематизированные Plotly-фигуры. Никаких хардкод-цветов в
компонентах.

## Структура модулей

### `assets/dashboard_theme.css`
Полная дизайн-система — единственный источник стилей DOM. Содержит
токены тем (`:root`, `html[data-theme="dark|light"]`), хедер, фильтр-
бар, KPI-карточки, карточки графиков, таблицу, name-displays и
адаптивные брейкпоинты. Dash подгружает `assets/` автоматически.

Темы переключаются установкой `data-theme="dark|light"` на `<html>` —
все цвета это CSS custom properties, поэтому смена атрибута
ретемизирует весь DOM без перерисовки компонентов.

### `plotly_templates.py`
Тематизированные построители фигур (единственный источник стилей
графиков). `ranked_bar` — столбцы с ранжированной прозрачностью,
значениями над столбцами и опциональным оверлеем Region Average на
вторичной оси. `age_groups` — стек RO по возрастным полосам + линия
AVG UIO. `build_dashboard_figures` собирает все 6 фигур под выбранную
тему. Токены `THEMES` держатся идентичными CSS — **меняешь цвет,
меняй в обоих местах**.

Plotly не читает CSS-переменные, поэтому фигуры перестраиваются на
стороне сервера под тему (см. `theme` в колбэке `update_dashboard`).

### `templates.py`
Минимальный `index_string`: стартовая тема через `data-theme`, импорт
JetBrains Mono. Весь дизайн — в `assets/`.

### `components.py`
Переиспользуемые компоненты на классах дизайн-системы:

- `_select_field()` / `create_*_selector()` — поля фильтр-бара
- `create_metric_card()` / `create_cards_row()` — KPI (`.kpi/.kpi.hero`)
- `create_chart_card()` — карточка графика (`.card`)
- `create_data_table()` — таблица (`.tablecard`, скрытие колонок
  после PPR, `model-chip`)
- name-displays и кнопка экспорта

### `functions.py`
Загрузка и обработка данных, метрики, сборка контейнеров. `create_
charts()` делегирует построение в `plotly_templates`.

### `dnm.py`
Layout и колбэки. Хедер с брендом и тумблером тем; clientside-колбэк
переключает `data-theme` на `<html>`, server-side колбэк
перестраивает фигуры под тему.

## Цветовые токены

| Токен | Dark | Light |
|---|---|---|
| `--accent` | `#BFC2BF` | `#05141f` |
| `--accent-2` (AVG UIO / region) | `#16AFC0` | `#16AFC0` |
| `--bg` | `#05141f` | `#eef1f4` |
| `--surface` | `#0c2230` | `#ffffff` |
| `--text` | `#eef4f8` | `#05141f` |

Бренд-основа — Kia Signature navy `#05141f` + белый. Шрифты:
KiaSignature (локальные woff2 в `assets/fonts/`) для UI, JetBrains
Mono с `tabular-nums` для чисел и таблиц.
