import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


@pytest.fixture(autouse=True)
def clear_loggers() -> Generator[None, None, None]:
    for name in [
        "read_excel",
        "greeting",
        "process_data",
        "get_detailed_info",
        "get_top_five_transactions",
        "get_currency_rate",
        "get_stoke_prices",
        "load_user_settings",
    ]:
        logger = logging.getLogger(name)
        logger.handlers.clear()
    yield


@pytest.fixture
def mock_excel_file(tmp_path: Path) -> Generator[dict[str, Any], None, None]:
    # Создаем путь до файла
    test_file = tmp_path / "test_transactions.xlsx"
    # Записываем тестовые данные
    sample_df = pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )
    # Записываем значения в виде excel
    sample_df.to_excel(test_file, index=False)

    mock_exists = MagicMock(return_value=True)
    patch_exists = patch("src.views.os.path.exists", new=mock_exists)

    mock_read_excel = MagicMock(return_value=sample_df)
    patch_read_excel = patch("src.views.pd.read_excel", new=mock_read_excel)

    with patch_exists, patch_read_excel:
        yield {
            "path": test_file,
            "filename": "test_transactions.xlsx",
            "expected_df": sample_df,
            "mock_exists": mock_exists,
            "mock_read_excel": mock_read_excel,
        }


@pytest.fixture
def table_excel(tmp_path: Path) -> pd.DataFrame:
    test_file = tmp_path / "operations.xlsx"

    dates = [
        datetime(2023, 1, 1),
        datetime(2023, 1, 2),
        datetime(2023, 1, 3),
    ]
    sample_df = pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Дата операции": dates,
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )
    sample_df.to_excel(test_file, index=False)

    return sample_df


@pytest.fixture
def table_excel_no_column(tmp_path: Path) -> pd.DataFrame:
    test_file = tmp_path / "operations.xlsx"

    sample_df = pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )
    sample_df.to_excel(test_file, index=False)

    return sample_df


@pytest.fixture
def table_excel_no_date(tmp_path: Path) -> pd.DataFrame:
    test_file = tmp_path / "operations.xlsx"

    sample_df = pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Дата операции": ["2023-03-01", "15/10/2023", "нет даты"],
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )
    sample_df.to_excel(test_file, index=False)

    return sample_df


@pytest.fixture
def data_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Дата операции": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )


@pytest.fixture
def data_frame_for_top_five() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788", "4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75, 500.0, 250.45, 420.22],
            "Категория": ["Продукты", "Транспорт", "Электроника", "Досуг", "Супермаркеты", "Различные товары"],
            "Дата платежа": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01", "2023-01-02", "2023-01-03"],
            "Описание": [
                "Перевод с карты",
                "Плата за оповещения об операциях",
                "Комиссия за операцию",
                "OZON",
                "Лента",
                "Яндекс.лавка",
            ],
        }
    )


@pytest.fixture
def data_frame_for_top_five_no_data() -> pd.DataFrame:
    return pd.DataFrame()


@pytest.fixture
def data_frame_for_top_five_no_data_1() -> pd.DataFrame:
    return pd.DataFrame({"top_transactions": []})


@pytest.fixture
def data_frame_without_column() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Сумма операции с округлением": [100.0, 200.5, 350.75],
            "Категория": ["Продукты", "Транспорт", "Электроника"],
            "Описание": ["Перевод с карты", "Плата за оповещения об операциях", "Комиссия за операцию"],
        }
    )


@pytest.fixture
def json_data_frame() -> str:
    result = {
        "cards": [
            {"last_digits": "4556", "total_spent": 100.0, "cashback": 1.0},
            {"last_digits": "5091", "total_spent": 200.5, "cashback": 2.0},
            {"last_digits": "7788", "total_spent": 350.75, "cashback": 3.51},
        ]
    }
    return json.dumps(result, indent=4)


@pytest.fixture
def result_data_frame_for_top_five() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "top_transactions": [
                {"date": "2023-01-01", "amount": 500.0, "category": "Досуг", "description": "OZON"},
                {
                    "date": "2023-01-03",
                    "amount": 420.22,
                    "category": "Различные товары",
                    "description": "Яндекс.лавка",
                },
                {
                    "date": "2023-01-03",
                    "amount": 350.75,
                    "category": "Электроника",
                    "description": "Комиссия за операцию",
                },
                {"date": "2023-01-02", "amount": 250.45, "category": "Супермаркеты", "description": "Лента"},
                {
                    "date": "2023-01-02",
                    "amount": 200.5,
                    "category": "Транспорт",
                    "description": "Плата за оповещения об операциях",
                },
            ]
        }
    )


@pytest.fixture
def currency_rate_data() -> str:
    return json.dumps(
        {"currency_rates": [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]}, indent=4
    )


@pytest.fixture
def stock_prices_data() -> str:
    return json.dumps({"stock_prices": [{"stock": "AAPL", "price": 226.8}, {"stock": "IBM", "price": 150.8}]})


@pytest.fixture
def dict_data() -> dict:
    return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}


@pytest.fixture
def data_frame_for_category_cashback() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Номер карты": ["4556", "5091", "7788", "4556", "5091", "7788"],
            "Сумма операции с округлением": [100.0, 200.5, 350.75, 500.0, 250.45, 420.22],
            "Категория": ["Продукты", "Транспорт", "Электроника", "Досуг", "Супермаркеты", "Различные товары"],
            "Дата платежа": ["01.01.2023", "05.01.2023", "01.03.2023", "09.01.2023", "01.02.2023", "20.03.2023"],
            "Описание": [
                "Перевод с карты",
                "Плата за оповещения об операциях",
                "Комиссия за операцию",
                "OZON",
                "Лента",
                "Яндекс.лавка",
            ],
        }
    )


@pytest.fixture
def spending_by_category_data() -> pd.DataFrame:
    return pd.DataFrame({
        "Дата платежа": [
            "01.01.2024", "05.02.2024", "10.03.2024",
            "20.04.2024", "30.05.2024"
        ],
        "Категория": [
            "Каршеринг", "каршеринг", "КАРШЕРИНГ",
            "Такси", "Еда"
        ],
        "Сумма операции с округлением": [500.0, 300.0, 200.0, 1000.0, 800.0]
    })
