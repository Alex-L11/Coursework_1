import logging
import pytest
import json
import pandas as pd
from datetime import datetime

from pandas import DataFrame
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def clear_loggers():
    for name in [
        'read_excel',
        'greeting',
        'process_data',
        'get_detailed_info',
        'get_top_five_transactions',
        'get_currency_rate',
        'get_stoke_prices',
        'load_user_settings'
    ]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
    yield


@pytest.fixture
def mock_excel_file(tmp_path):
    # Создаем путь до файла
    test_file = tmp_path / 'test_transactions.xlsx'
    # Записываем тестовые данные
    sample_df = pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })
    # Записываем значения в виде excel
    sample_df.to_excel(test_file, index=False)

    mock_exists = MagicMock(return_value=True)
    patch_exists = patch("src.views.os.path.exists", new=mock_exists)

    mock_read_excel = MagicMock(return_value=sample_df)
    patch_read_excel = patch('src.views.pd.read_excel', new=mock_read_excel)

    with patch_exists, patch_read_excel:
        yield {
            'path': test_file,
            'filename': 'test_transactions.xlsx',
            'expected_df': sample_df,
            'mock_exists': mock_exists,
            'mock_read_excel': mock_read_excel
        }


@pytest.fixture
def table_excel(tmp_path):
    test_file = tmp_path / 'operations.xlsx'

    dates = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3),


    ]
    sample_df = pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Дата операции": dates,
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })
    sample_df.to_excel(test_file, index=False)

    return sample_df

@pytest.fixture
def table_excel_no_column(tmp_path):
    test_file = tmp_path / 'operations.xlsx'

    dates = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3),


    ]
    sample_df = pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })
    sample_df.to_excel(test_file, index=False)

    return sample_df


@pytest.fixture
def table_excel_no_date(tmp_path):
    test_file = tmp_path / 'operations.xlsx'

    sample_df = pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Дата операции": ['2023-03-01', '15/10/2023', 'нет даты'],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })
    sample_df.to_excel(test_file, index=False)

    return sample_df


@pytest.fixture
def data_frame():
    return pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03"],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })

@pytest.fixture
def data_frame_for_top_five():
    return pd.DataFrame({
        "Номер карты": ["4556", "5091", "7788", "4556", "5091", "7788"],
        "Сумма операции с округлением": [100.0, 200.5, 350.75, 500.0, 250.45, 420.22],
        "Категория": ["Продукты", "Транспорт", "Электроника", "Досуг", "Супермаркеты", "Различные товары"],
        "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01", "2023-01-02", "2023-01-03"],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию', "OZON", "Лента", "Яндекс.лавка" ]
    })


@pytest.fixture
def data_frame_for_top_five_no_data():
    return pd.DataFrame()


@pytest.fixture
def data_frame_for_top_five_no_data_1():
    return pd.DataFrame({'top_transactions': []})


@pytest.fixture
def data_frame_without_column():
    return pd.DataFrame({
        "Сумма операции с округлением": [100.0, 200.5, 350.75],
        "Категория": ["Продукты", "Транспорт", "Электроника"],
        "Описание": ['Перевод с карты', 'Плата за оповещения об операциях', 'Комиссия за операцию']
    })


@pytest.fixture
def json_data_frame():
    result = {
        'cards': [
            {
                'last_digits': '4556',
                'total_spent': 100.0,
                'cashback': 1.0
            },
            {
                'last_digits': '5091',
                'total_spent': 200.5,
                'cashback': 2.0
            },
            {
                'last_digits': '7788',
                'total_spent': 350.75,
                'cashback': 3.51
            }
        ]
    }
    return json.dumps(result, indent=4)

@pytest.fixture
def result_data_frame_for_top_five():
    return pd.DataFrame({
        'top_transactions': [
            {
                'date': '2023-01-01',
                'amount': 500.0,
                'category': "Досуг",
                'description': "OZON"
            },
            {
                'date': '2023-01-03',
                'amount': 420.22,
                'category': "Различные товары",
                'description': "Яндекс.лавка"
            },
            {
                'date': '2023-01-03',
                'amount': 350.75,
                'category': "Электроника",
                'description': "Комиссия за операцию"
            },
            {
                'date': '2023-01-02',
                'amount': 250.45,
                'category': "Супермаркеты",
                'description': "Лента"
            },
            {
                'date': '2023-01-02',
                'amount': 200.5,
                'category': "Транспорт",
                'description': "Плата за оповещения об операциях"
            }

        ]
    })


@pytest.fixture
def currency_rate_data():
    return json.dumps({"currency_rates": [
    {
      "currency": "USD",
      "rate": 73.21
    },
    {
      "currency": "EUR",
      "rate": 87.08
    }]}, indent=4)


@pytest.fixture
def stock_prices_data():
    return json.dumps({"stock_prices": [
        {
        "stock": "AAPL",
        "price": 226.8
        },
        {
            "stock": "IBM",
            "price": 150.8
        }]})


@pytest.fixture
def dict_data():
    return {
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}