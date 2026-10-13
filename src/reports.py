import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)
log_dir = os.path.join(root_dir, 'logs')
log_file = os.path.join(log_dir, 'reports.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    filename=log_file,
                    filemode='w',
                    encoding='utf-8')

spend_by_cat_logger = logging.getLogger('spending_by_category')


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """ Принимает датафрейм с транзакциями, название категории и опциональную дату, возвращает результат в файл. """
    if not isinstance(transactions, pd.DataFrame):
        spend_by_cat_logger.error('Данные не DataFrame')
        raise TypeError('Данные не формата DataFrame')

    if not isinstance(category, str):
        spend_by_cat_logger.error('category не строка')
        raise TypeError('Аргумент "category" должен быть строкой')
    spend_by_cat_logger.info('Делаем выборку по "Дате платежа", "Категория", "Сумма операции с округлением"')

    try:
        trans_df = transactions[['Дата платежа', 'Категория', 'Сумма операции с округлением']]
    except KeyError:
        spend_by_cat_logger.error('Нет нужной колонки')
        raise ValueError('В данных нет нужной колонки') from None

    spend_by_cat_logger.info('Сортируем согласно выбранной категории')
    cat_norm = category.casefold()
    mask = (
        trans_df['Категория'].notna() &
        (trans_df['Категория'].astype(str).str.casefold() == cat_norm)
    )
    df = trans_df.loc[mask]

    if df.empty:
        spend_by_cat_logger.warning('Транзакций по категории нет')
        return pd.DataFrame(columns=['Дата платежа', 'Категория', 'Сумма операции с округлением'])

    # result_df = df

    if date is None:
        spend_by_cat_logger.info('Дата не указана, используем текущую')
        dt = pd.Timestamp.today() - pd.DateOffset(years=5)
    else:
        s = str(date).strip()
        if len(s) != 10 or s[2] != '.' or s[5] != '.':
            spend_by_cat_logger.error('Неккоректный формат даты')
            raise ValueError(f'Неккоректный формат даты: {date}. Нужен формат ДД.ММ.ГГГГ')

        day_part = s[0:2]
        month_part = s[3:5]
        year_part = s[6:10]

        if not (day_part.isdigit() and month_part.isdigit() and year_part.isdigit()):
            spend_by_cat_logger.error('Дата должна состоять из цифр')
            raise ValueError('Дата должна состоять из цифр')

        try:
            dt = pd.to_datetime(s, dayfirst=True)
            if pd.isna(dt):
                spend_by_cat_logger.error('Не удалось распарсить дату')
                raise ValueError('Не удалось распарсить дату')
        except ValueError:
            spend_by_cat_logger.error('Ошибка парсинга даты')
            raise ValueError('Ошибка фильтрации по дате')

    col = 'Дата платежа'
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        spend_by_cat_logger.info('конвертируем столбец "Дата платежа" в datetime')
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        # Удаляем строки, где дата не конвертнулась
        df = df.dropna(subset=[col])

    # Вычисляем 3 месяца назад
    start_date = dt - pd.DateOffset(months=3)

    # Получаем данные в диапозоне 3 месяцево от start_date до полученной даты
    range_date = (df['Дата платежа'] >= start_date) & (df['Дата платежа'] <= dt)

    spend_by_cat_logger.info("Получаем конечную таблицу")
    result_df = df[range_date].copy()

    return result_df


if __name__ == '__main__':
    # Получаем папку, где лежит скрипт
    dir_script = Path(__file__).resolve().parent
    # Идем в корень проекта
    file_path_excel = dir_script.parent / 'data' / 'operations.xlsx'

    try:
        df_from_excel = pd.read_excel(file_path_excel)
    except FileNotFoundError:
        raise FileNotFoundError('Файл не найден')

    result = spending_by_category(df_from_excel, "Супермаркеты")
    print(result)
