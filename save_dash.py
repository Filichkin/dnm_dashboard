import os
import subprocess
import time

import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from dnm import (
    fig_profit, fig_mh, fig_avg_mh, fig_avg_check, fig_ratio, fig_ro_years, df
)

# Для скриншота браузера
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium не установлен. Для скриншота браузера "
          "установите: pip install selenium")


def start_dashboard_server():
    """Запускает дашборд в фоновом режиме"""
    try:
        # Запускаем дашборд в отдельном процессе
        process = subprocess.Popen(
            ['python', 'dnm.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Ждём запуска сервера
        time.sleep(5)
        return process
    except Exception as e:
        print(f"Ошибка запуска дашборда: {e}")
        return None


def save_plotly_fig(fig, filename):
    fig.write_image(filename, width=900, height=500, scale=2)


def save_table_as_image(df, filename):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    df_table = df
    if 'total_0_10' in df_table.columns:
        df_table = df_table[df_table['total_0_10'] != 0]
    df_table = (
        df_table.sort_values('total_ro_cost', ascending=False)
        if 'total_ro_cost' in df_table.columns else df_table
    )

    priority_cols = [
        'model',
        'uio_10y',
        'total_0_10',
        'total_ro_cost',
        'avg_ro_cost',
        'labor_hours_0_10',
        'aver_labor_hours_per_vhc',
        'labor_amount_0_10',
        'avg_ro_labor_cost',
        'parts_amount_0_10',
        'avg_ro_part_cost',
    ]
    ordered_cols = (
        [c for c in priority_cols if c in df_table.columns] +
        [c for c in df_table.columns if c not in priority_cols]
    )
    df_table = df_table[ordered_cols]
    tbl = ax.table(
        cellText=df_table.head(20).values,
        colLabels=df_table.columns,
        loc='center',
        cellLoc='center',
        colLoc='center',
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(6)
    tbl.auto_set_column_width(col=list(range(len(df_table.columns))))
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=200)
    plt.close(fig)


def capture_dashboard_screenshot(
    url='http://127.0.0.1:8050/',
    output_file='dashboard_screenshot.png'
):
    """Создаёт скриншот дашборда как он отображается в браузере"""
    if not SELENIUM_AVAILABLE:
        print("Selenium недоступен. Используйте обычный метод сохранения.")
        return False
    
    try:
        # Настройки Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Без GUI
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Ждём загрузки (можно увеличить время если нужно)
        time.sleep(3)
        
        # Делаем скриншот
        driver.save_screenshot(output_file)
        driver.quit()
        
        print(f"Скриншот сохранён как {output_file}")
        return True
        
    except Exception as e:
        print(f"Ошибка при создании скриншота: {e}")
        return False


def save_dashboard_to_pdf(pdf_path='dashboard.pdf'):
    figs = [
        ('ТОП-10 по общей прибыли (total_ro_cost)', fig_profit),
        ('ТОП-10 по общим нормо-часам (labor_hours_0_10)', fig_mh),
        ('ТОП-10 по средним нормо-часам на автомобиль', fig_avg_mh),
        ('ТОП-10 по среднему чеку (avg_ro_cost)', fig_avg_check),
        ('ТОП-10 по соотношению RO/UIO (ro_ratio_of_uio_10y)', fig_ratio),
        ('Количество заказ-нарядов по возрастным группам', fig_ro_years),
    ]
    img_files = []
    for i, (title, fig) in enumerate(figs):
        fname = f'_tmp_fig_{i}.png'
        save_plotly_fig(fig, fname)
        img_files.append((title, fname))

    table_img = '_tmp_table.png'
    save_table_as_image(df, table_img)
    img_files.append(('Таблица данных (первые 20 строк)', table_img))

    # Создаём PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    for title, img in img_files:
        c.setFont('Helvetica-Bold', 14)
        c.drawString(40, height - 40, title)
        c.drawImage(
            ImageReader(img), 40, 100, width=520,
            preserveAspectRatio=True, mask='auto'
        )
        c.showPage()
    c.save()

    for _, img in img_files:
        if os.path.exists(img):
            os.remove(img)


def save_dashboard_as_single_page(pdf_path='dashboard_single_page.pdf'):
    """Сохраняет дашборд как одну страницу PDF из скриншота браузера"""
    screenshot_file = 'dashboard_screenshot.png'
    
    # Запускаем дашборд автоматически
    print("Запускаем дашборд...")
    dashboard_process = start_dashboard_server()
    
    if dashboard_process is None:
        print("Не удалось запустить дашборд. Используйте обычный метод.")
        return
    
    try:
        if capture_dashboard_screenshot(output_file=screenshot_file):
            # Создаём PDF с одной страницей
            c = canvas.Canvas(pdf_path, pagesize=A4)
            width, height = A4
            
            # Добавляем заголовок
            c.setFont('Helvetica-Bold', 16)
            c.drawString(40, height - 40, 'DNM RO DATA by models')
            
            # Добавляем скриншот
            c.drawImage(
                ImageReader(screenshot_file), 40, 60, width=width-80,
                preserveAspectRatio=True, mask='auto'
            )
            c.save()
            
            # Удаляем временный файл
            if os.path.exists(screenshot_file):
                os.remove(screenshot_file)
            
            print(f"Дашборд сохранён как одна страница: {pdf_path}")
        else:
            print("Не удалось создать скриншот. Используйте обычный метод.")
    
    finally:
        # Останавливаем дашборд
        if dashboard_process:
            dashboard_process.terminate()
            print("Дашборд остановлен.")


if __name__ == '__main__':
    # Выберите один из методов:
    
    # 1. Обычный метод (отдельные страницы для каждого графика)
    # save_dashboard_to_pdf('dnm_dashboard.pdf')
    # print('PDF сохранён как dnm_dashboard.pdf')
    
    # 2. Метод одной страницы (автоматически запускает дашборд)
    save_dashboard_as_single_page('dnm_dashboard_single.pdf')
    print('Одностраничный PDF сохранён как dnm_dashboard_single.pdf')
