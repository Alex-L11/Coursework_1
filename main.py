import json
from datetime import datetime


from src.views import (greeting, get_detailed_info, get_top_five_transactions, get_currency_rates,
                       get_stock_prices, process_data, load_user_settings)


def main(date_str: str) -> str:
    """Функция принимает строку с датой и временем в формате YYYY-MM-DD HH:MM:SS и возвращает JSON-ответ со следующими
    данными: последние 4 цифры карты, общая сумма расходов, кэшбек (1рубль на каждые 100рублей)"""
    # Получаем дату в ожидаемом формате
    try:
        date_operation = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError as e:
        raise ValueError(f'Неверный формат даты, ожидается формат YYYY-MM-DD HH:MM:SS. Ошибка: {e}')

    # Получаем входные данные для курса валют и акций
    settings = load_user_settings('user_setting.json')
    user_currencies = settings['user_currencies']
    user_stocks = settings['user_stocks']

    # Приветсвие
    greet = greeting()

    # Данные по операциям с 1 числа по указанную дату
    df = process_data(date_operation)

    # Детализация операций по картам(последние 4 цифры, сумма, кешбэк)
    detailed_json_str = get_detailed_info(df)
    # Парсим данные в словарь, чтобы взять данные по ключу "cards"
    detailed_data = json.loads(detailed_json_str)
    cards = detailed_data.get('cards', [])

    # Топ-5 транзакций
    top_json_str = get_top_five_transactions(df)
    # Парсим данные в словарь, чтобы взять данные по ключу "top_transactions"
    top_data = json.loads(top_json_str)
    top_transactions = top_data.get('top_transactions', [])

    # Курсы валют
    currency_data = json.loads(get_currency_rates(user_currencies))
    currency_rates = currency_data.get('currency_rates', [])

    # Цены акций

    stock_data = json.loads(get_stock_prices(user_stocks))
    stock_prices = stock_data.get('stock_prices', [])

    result = {
        "greeting": greet,
        'cards': cards,
        'top_transactions': top_transactions,
        'currency_rates': currency_rates,
        'stock_prices': stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    input_date = '2021-10-15 14:30:00'
    print(main(input_date))


