import json
import os
import pandas as pd
import datetime
import logging
from datetime import datetime

from black.trans import defaultdict

from src.views import read_excel

base_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(base_dir)
log_dir = os.path.join(root_dir, 'logs')
log_file = os.path.join(log_dir, 'services.log')
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s: %(message)s',
                    filename=log_file,
                    filemode='w',
                    encoding='utf-8')

cat_cash_logger = logging.getLogger('category_cashback')

def category_cashback(data: str, year: int, month: int) -> str:
    """
    Принимает данные с трназакциями, год за который проводится анализ и месяц, за который проводится анализ,
    выдает JSON с анализом, сколько на каждой категории можно заработать кэшбека.
    """
    result_dict = defaultdict(float)
    # Проверяем тип данных
    if not isinstance(year, int) or not isinstance(month, int):
        cat_cash_logger.error('Данные не числовые значения')
        raise TypeError('Введите год и месяц числами')
    # Получаем файл с данными
    try:
        cat_cash_logger.info('Читаем файл с данными')
        data_trans_df = read_excel(data)
        trans_dict = data_trans_df.to_dict(orient='records')
        cat_cash_logger.info('Выбираем из данных только интересующие колонки')

        for trans in trans_dict:
            date = trans.get('Дата платежа')
            category = trans.get('Категория')
            amount = trans.get('Сумма операции с округлением')

            # Пропускаем не подходящие значения
            if date is None or category is None or amount is None:
                continue

            dt = None
            # Приводим даты к datetime
            if isinstance(date, datetime):
                dt = date
            else:
                # Парсим если строка
                try:
                    dt = datetime.strptime(str(date).strip(), '%d.%m.%Y')
                except ValueError:
                    cat_cash_logger.error('Значения даты не подходят, пропускаем эти строки')
                    continue

            if dt is None:
                continue

            # Фильтрация по году и месяцу
            if dt.year != year or dt.month != month:
                continue

            try:
                amount_float = float(amount)
                result_dict[category] += amount_float
            except TypeError:
                cat_cash_logger.error('Ошибка в типе суммы')
                continue

    except ValueError as ex:
        print(f'Ошибка: {ex}')

    final_result = {}
    cat_cash_logger.info('Формаируем новый словарь для вывод кэшбека')
    for cat, total in result_dict.items():
        total_round = round(total)
        cashback = total_round // 100
        final_result[cat] = cashback

    sorted_cashback = sorted(final_result.items(), key=lambda x: x[1], reverse=True)
    sorted_dict = dict(sorted_cashback)
    cat_cash_logger.info('Возвращаем готовый словарь в json-строке')
    return json.dumps(sorted_dict, ensure_ascii=False, indent=4)
