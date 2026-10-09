import os
import json
import pandas as pd
import requests
import time
import logging

from pandas import DataFrame
from datetime import datetime
from bisect import bisect
from dotenv import load_dotenv
from logging import Logger
from typing import Dict, List, Any

load_dotenv()

DATETIME_FORMAT_DMY_HMS = "%d.%m.%Y %H:%M:%S"


def setup_logger(name: str, log_file: str, level=logging.INFO) -> Logger:
    """
    Функкция принимает имя функции, файл-логер и записывает логи для каждой функции в отдельный файл с именем этой
    функции
    """
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

logger_read_excel = setup_logger('read_excel', 'read_excel.log')
logger_greeting = setup_logger('greeting', 'greeting.log')
logger_process_data = setup_logger('process_data', 'process_data.log')
logger_get_detailed_info = setup_logger('get_detailed_info', 'get_detailed_info.log')
logger_get_top_five_transactions = setup_logger('get_top_five_transactions', 'get_top_five_transactions.log')
logger_get_currency_rates = setup_logger('get_currency_rates', 'get_currency_rates.log')
logger_get_stoke_prices = setup_logger('get_stoke_prices', 'get_stoke_prices.log')
logger_load_user_settings = setup_logger('load_user_settings', 'load_user_settings.log')

def read_excel(data_xlsx: str) -> DataFrame:
    """ Принимает путь к файлу Excel и выдает dataframe. """
    # папка где лежит проект
    base_dir = os.path.dirname(__file__)

    # поднимаемся в корень проекта
    project_root = os.path.dirname(base_dir)

    # собираем путь до файла целиком
    data_path = os.path.join(project_root, 'data', data_xlsx)
    if not os.path.exists(data_path):
        logger_read_excel.info('Файл не найден')
        raise FileNotFoundError(f'Файл не найден: {data_xlsx}')
    try:
        logger_read_excel.info(f'Открываем excel файл, который находится в {data_xlsx}')
        data_frame = pd.read_excel(data_path)
        return data_frame
    except ValueError:
        logger_read_excel.error('Произошла ошибка ValueError')
        raise ValueError('Файл пустой или содержит некорректные данные')


def greeting() -> str:
    """
    Функция возвращает «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи»
    в зависимости от текущего времени.
    """
    logger_greeting.info('Получаем дату и время на момент запроса')
    hour = datetime.now().hour

    boundaries = [0, 6, 12, 18]
    greetings = [
        "Доброй ночи",
        "Доброе утро",
        "Добрый день",
        "Добрый вечер",
    ]
    logger_greeting.info('Вывод сообщения согласно времени суток')
    return greetings[bisect(boundaries, hour) - 1]


def process_data(date_operation: datetime) -> pd.DataFrame:
    """
    Принимает дату операции, возвращает данные с 1-го числа месяца до даты операции включительно.
    """
    # Вычисляем начало месяца по введенной дате, оно будет началом диапозна
    date_start = date_operation.replace(day=1, hour=0, minute=0, second=0)
    # Конец диапозна
    date_end = date_operation

    data = read_excel('operations.xlsx')
    logger_process_data.info('Приведение столбца "Дата операции" к формату даты')
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], format=DATETIME_FORMAT_DMY_HMS)

    result_data =  data.query('@date_start <= `Дата операции` <= @date_end')

    result_data.sort_values('Дата операции', inplace=True)
    logger_process_data.info(f'Вывод банковских операций с 1 дня месяца по {date_operation}')
    return result_data


def get_detailed_info(result_data: pd.DataFrame) -> str:
    """
    Принимает данные DataFrame и агрегирует в формат:
    - последние 4 цифры карты
    - общая сумма расходов
    - кешбэк (1 рубль на каждые 100 рублей)
    """
    logger_get_detailed_info.info('Из таблицы оставялем два столбца: "Номер карты" и "Сумма операции с округлением"')
    # выбираем колонки "Номер карты" и "Сумма операции с округлением"
    df = result_data[['Номер карты', 'Сумма операции с округлением']]
    # в колонке "Номер карты" убираем знак "*"
    df['Номер карты'] = df['Номер карты'].str[1:]

    # группируем и суммируем
    df_new = df.groupby('Номер карты', as_index=False)['Сумма операции с округлением'].sum()
    # добавление нового столбца "cashback" и
    df_new['cashback'] = (df_new['Сумма операции с округлением'] / 100).round(2)
    logger_get_detailed_info.info(f'Переводим DataFrame в словарь')
    result_dict = df_new.to_dict(orient='records')

    card_list = []
    logger_get_detailed_info.info(f'Формируем новый список словарей {card_list}')
    for card in result_dict:
        card_list.append({
            'last_digits': card['Номер карты'],
            'total_spent': card['Сумма операции с округлением'],
            'cashback': card['cashback']
        })
    card_list = {'cards': card_list}

    return json.dumps(card_list, indent=4)


def get_top_five_transactions(result_data: pd.DataFrame) -> str:
    """
    Принимает DataFrame с трансакциями, возвращает топ-5 транзакций по сумме платежей ввиде:
    "top_transactions": [
    {
      "date": "21.12.2021",
      "amount": 1198.23,
      "category": "Переводы",
      "description": "Перевод Кредитная карта. ТП 10.2 RUR"
    }
    """
    logger_get_top_five_transactions.info('Делаем выборку столбцов: "Дата платежа",'
                                          '"Сумма операции с округлением", "Категория", "Описание"')
    df = result_data[['Дата платежа', 'Сумма операции с округлением', 'Категория', 'Описание']]
    # группируем
    trans_group = df.sort_values('Сумма операции с округлением', ascending=False).head(5)
    logger_get_top_five_transactions.info(f'Переводим DataFrame в словарь')
    trans_group_dict = trans_group.to_dict(orient='records')

    five_trans = []
    logger_get_top_five_transactions.info(f'Формируем новый списк словарей {five_trans}')
    for trans in trans_group_dict:
        five_trans.append({
            'date': trans['Дата платежа'],
            'amount': round(trans['Сумма операции с округлением'], 2),
            'category': trans['Категория'],
            'description': trans['Описание']
        })

    five_trans = {'top_transactions': five_trans}

    return json.dumps(five_trans, ensure_ascii=False, indent=4)


def get_currency_rates(currency_code: List) -> str:
    """Принимает список валют, возвращает курс валют в json"""
    url = f'https://www.cbr-xml-daily.ru//daily_json.js'
    logger_get_currency_rates.info('Делаем API запрос')
    response = requests.get(url)
    if response.status_code != 200:
        logger_get_currency_rates.error('Ошибка при получении курса валюты')
        raise ValueError(f'Ошибка при получении курса валюты')
    data = response.json()
    logger_get_currency_rates.info('Получаем информацию по валютам')
    currency_data = data.get('Valute', {})
    if not currency_data:
        logger_get_currency_rates.error('Нет данных о валюте')
        raise ValueError('Нет данных для конвертации валюты')

    result = []

    logger_get_currency_rates.info(f'Формируем новый список словарей {result}')
    for code in currency_code:
        code_upper = code.upper()
        info = currency_data.get(code_upper)
        if not info:
            continue
        result.append({
            'currency': code_upper,
            'rate': float(round(info['Value'], 2))
        })
    result = {'currency_rates': result}

    return json.dumps(result, indent=4)


def get_stock_prices(symbols: List) -> str:
    """Принимает список наименований акций, возвращает наименование и стоимость акции в json"""
    logger_get_stoke_prices.info('Получаем API ключ')
    api_key = os.getenv('API_KEY')
    if not api_key:
        logger_get_stoke_prices.error(f'Нет ключа: {api_key}')
        raise ValueError('Нет API ключа')

    result = []
    errors = []
    logger_get_stoke_prices.info('По каждой акции отлельно делаем запрос')
    for i, symbol in enumerate(symbols):
        symbol_upper = symbol.upper()
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol_upper}&apikey={api_key}'

        if i > 0:
            time.sleep(12)

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()

            if 'Information' in data:
                logger_get_stoke_prices.error('Большая частота запросов, больше 1 запроса в секунду)')
                errors.append(f'{symbol_upper}: лимит API - {data['Information']}')
                continue

            if 'Error Message' in data:
                logger_get_stoke_prices.error('Ошибка запроса')
                raise ValueError(f'Ошибка от API для {symbol_upper}: {data['Error Message']}')
            if 'Note' in data:
                logger_get_stoke_prices.error('Конец лимита на запросы')
                raise ValueError(f'Примечание от API для {symbol_upper}: {data['Note']}')

            time_series_key = 'Time Series (Daily)'
            if time_series_key not in data:
                logger_get_stoke_prices.error(f'Нет таймсерии для {symbol_upper}')
                raise ValueError(f'Не найдена таймсерия для {symbol_upper}')

            series = data[time_series_key]
            if not series:
                logger_get_stoke_prices.error(f'Нет данных в таймсерии для {symbol_upper}')
                raise ValueError(f'Нет данных таймсерии для {symbol_upper}')

            # выбираем словарь с последней датой
            latest_date = next(iter(series))
            latest_record = series[latest_date]

            adjust_close_str = latest_record.get('4. close')
            if adjust_close_str is None:
                logger_get_stoke_prices.error(f'Нет стоимости акции')
                raise ValueError(f'Не найдено поле "4. close" для {symbol_upper}')

            price = float(adjust_close_str)

            result.append({
                'stock': symbol_upper,
                'price': round(price, 2)
            })
        except requests.RequestException as e:
            logger_get_stoke_prices.error(f'Для {symbol_upper}: сетевая ошибка - {e}')
            errors.append(f'{symbol_upper}: сетевая ошибка - {e}')
            continue

    final_result = {'stock_prices': result}

    if errors:
        final_result['errors'] = errors

    return json.dumps(final_result, ensure_ascii=False, indent=4)


def load_user_settings(settings_path: str) -> dict[str, Any]:
    """Принимает путь до файла, читает данные из user_settings.json и возвращает словарь с данными"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', settings_path)

    try:
        logger_load_user_settings.info('Открытие файла')
        with open(file_path, "r", encoding="utf-8") as file_settings:
            try:
                logger_load_user_settings.info('Перевод json-строки в словарь')
                settings_data = json.load(file_settings)
                if not isinstance(settings_data, dict):
                    return {}
                logger_load_user_settings.info('Вывод словаря с валютами и акциями')
                user_currencies = settings_data.get('user_currencies', {})
                user_stocks = settings_data.get('user_stocks', {})
                return {'user_currencies': user_currencies,
                        'user_stocks': user_stocks,
                        }
            except json.JSONDecodeError:
                logger_load_user_settings.error('Произошла ошибка "JSONDEcodeError')
                print('Ошибка декодирования файла')
                return {}
    except FileNotFoundError:
        logger_load_user_settings.error('Ошибка "FileNotFoundError"')
        print("Файл не найден")
        return {}
