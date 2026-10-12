import json
import logging
import os
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from src.views import (
    get_currency_rates,
    get_detailed_info,
    get_stock_prices,
    get_top_five_transactions,
    greeting,
    load_user_settings,
    logger_process_data,
    process_data,
    read_excel,
    setup_logger,
)


@patch("logging.FileHandler")
def test_setup_logger_creates_handler(mock_file_handler: Mock) -> None:
    # Заменяем FileHandler
    handler_instance = Mock()
    mock_file_handler.return_value = handler_instance

    logger = setup_logger("test_logger", "test.log")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    expected_logs_dir = os.path.join(base_dir, "logs")
    expected_logs_path = os.path.join(expected_logs_dir, "test.log")

    # Проверяем, что FileHandler вызван с нужным путём и кодировкой
    mock_file_handler.assert_called_once_with(expected_logs_path, encoding="utf-8")

    # Проверяем, что setFormatter был вызван один раз
    assert handler_instance.setFormatter.call_count == 1

    # Прверяем, что к handler применили форматер и проверяем его формат
    formatter = handler_instance.setFormatter.call_args[0][0]
    assert formatter._fmt == "%(asctime)s - %(name)s - %(levelname)s: %(message)s"

    # Проверяем логгер
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO


def test_read_excel_success(mock_excel_file: dict) -> None:
    # Из словаря в фикстуре берем значение по ключу "filename"
    filename = mock_excel_file["filename"]
    # Берем из слваря тествые данные, которые будем сравнивать
    expected_df = mock_excel_file["expected_df"]
    # Вызываем тестируемую функцию с именем файла
    result_df = read_excel(filename)

    assert isinstance(result_df, pd.DataFrame)
    assert list(result_df.columns) == list(expected_df.columns)
    assert result_df.shape == expected_df.shape
    assert result_df["Сумма операции с округлением"].sum() == pytest.approx(651.25)


@pytest.mark.parametrize(
    "hour, expected_greeting",
    [
        (0, "Доброй ночи"),
        (3, "Доброй ночи"),
        (6, "Доброе утро"),
        (11, "Доброе утро"),
        (14, "Добрый день"),
        (16, "Добрый день"),
        (18, "Добрый вечер"),
        (23, "Добрый вечер"),
    ],
)
def test_greeting(hour: int, expected_greeting: str) -> None:
    # Мокаем datetime.now
    with patch("src.views.datetime") as mock_datetime:
        # Создаем объект datetime с нужным часом
        mock_now = datetime(2026, 1, 15, hour=hour, minute=30, second=30)
        mock_datetime.now.return_value = mock_now

        result = greeting()

        assert result == expected_greeting


@patch("src.views.read_excel")
def test_process_data_empty(mock_read: Mock, table_excel: pd.DataFrame) -> None:
    mock_read.return_value = table_excel
    test_datetime = datetime(2023, 1, 3, 10, 0, 0)
    result = process_data(test_datetime)

    assert result.equals(table_excel)

    mock_read.assert_called()
    mock_read.assert_called_once()


@patch.object(logger_process_data, "error")
@patch("src.views.read_excel")
def test_process_data_key_error(mock_read: Mock, mock_error: Mock, table_excel_no_column: pd.DataFrame) -> None:
    mock_read.return_value = table_excel_no_column
    test_datetime = datetime(2023, 1, 3, 10, 0, 0)

    result = process_data(test_datetime)

    assert result.empty
    mock_read.assert_called_once()
    assert 'Ошибка: отсутствует колонка "Дата операции"' in mock_error.call_args[0][0]


@patch.object(logger_process_data, "error")
@patch("src.views.read_excel")
def test_process_data_value_error(mock_read: Mock, mock_error: Mock, table_excel_no_date: pd.DataFrame) -> None:
    mock_read.return_value = table_excel_no_date
    test_datetime = datetime(2023, 1, 3, 10, 0, 0)
    result = process_data(test_datetime)

    assert result.empty
    mock_read.assert_called_once()

    assert "Ошибка формата даты" in mock_error.call_args[0][0]


@patch.object(logger_process_data, "error")
@patch("src.views.read_excel")
def test_process_data_exception_error(mock_read: Mock, mock_error: Mock) -> None:
    mock_read.side_effect = RuntimeError("Тестовая ошибка")

    test_datetime = datetime(2023, 1, 3, 10, 0, 0)
    result = process_data(test_datetime)

    assert result.empty
    mock_read.assert_called_once()
    log_message = mock_error.call_args[0][0]

    assert log_message.startswith("Неизвестная ошибка")


def test_get_detailed_info_success(data_frame: pd.DataFrame, json_data_frame: str) -> None:
    result = get_detailed_info(data_frame)

    assert result == json_data_frame


def test_get_detailed_info_without_column(data_frame_without_column: pd.DataFrame) -> None:
    result = get_detailed_info(data_frame_without_column)
    res = json.dumps({"cards": []})
    assert result == res


def test_detailed_info_type_error() -> None:
    df = pd.DataFrame(columns=["Номер карты", "Сумма операции с круглением"])
    result = get_detailed_info(df)

    res = json.dumps({"cards": []}, indent=4)
    assert result == res


def test_get_top_five_transactions_success(
    data_frame_for_top_five: pd.DataFrame, result_data_frame_for_top_five: pd.DataFrame
) -> None:
    result = get_top_five_transactions(data_frame_for_top_five)

    res: list[Any] = result_data_frame_for_top_five["top_transactions"].tolist()
    res_dict = {"top_transactions": res}
    res_str = json.dumps(res_dict, ensure_ascii=False, indent=4, sort_keys=True)
    result_str = json.dumps(json.loads(result), ensure_ascii=False, indent=4, sort_keys=True)

    assert result_str == res_str


def test_get_top_five_transactions_without_column(
    data_frame_without_column: pd.DataFrame,
    data_frame_for_top_five_no_data: pd.DataFrame,
) -> None:
    result_1 = get_top_five_transactions(data_frame_without_column)
    result_2 = get_top_five_transactions(data_frame_for_top_five_no_data)

    df = pd.DataFrame({"not": ["DataFrame"]})
    result_3 = get_top_five_transactions(df)

    assert result_1 == json.dumps({"top_transactions": []})
    assert result_2 == json.dumps({"top_transactions": []})
    assert result_3 == json.dumps({"top_transactions": []})


@patch("src.views.requests.get")
def test_get_currency_rates_success(mock_get: Mock, currency_rate_data: str) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 73.2121}, "EUR": {"Value": 87.0842}}}
    mock_get.return_value = mock_response
    result = get_currency_rates(["USD", "EUR"])

    assert result == currency_rate_data


@patch("src.views.requests.get")
def test_get_currency_rates_value_error(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 300

    mock_get.return_value = mock_response
    with pytest.raises(ValueError, match="Ошибка при получении курса валюты"):
        get_currency_rates(["USD", "EUR"])


@patch("src.views.requests.get")
def test_get_currency_rates_value_error_1(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200

    mock_response.json.return_value = {"OtherKey": "value"}
    mock_get.return_value = mock_response
    with pytest.raises(ValueError, match="Нет данных для конвертации валюты"):
        get_currency_rates(["USD"])


@patch("src.views.requests.get")
def test_get_currency_rates_without_data(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Valute": {"USD": {"Value": 73.2121}, "EUR": {"Value": 87.0842}}}
    mock_get.return_value = mock_response
    result = get_currency_rates([])

    assert result == json.dumps({"currency_rates": []}, indent=4)


@patch("src.views.os.getenv")
@patch("src.views.time.sleep")
@patch("src.views.requests.get")
def test_get_stock_prices_success(mock_get: Mock, mock_time_sleep: Mock, mock_getenv: Mock) -> None:
    mock_getenv.return_value = "api_key"
    aapl_data = {
        "Meta Data": {"1. Information": "Daily Prices", "2. Symbol": "AAPL"},
        "Time Series (Daily)": {"2024-06-10": {"4. close": "226.8000"}},
    }
    ibm_data = {
        "Meta Data": {"1. Information": "Daily Prices", "2. Symbol": "IBM"},
        "Time Series (Daily)": {"2024-06-10": {"4. close": "150.8000"}},
    }
    mock_aapl_resp = Mock()
    mock_aapl_resp.status_code = 200
    mock_aapl_resp.json.return_value = aapl_data

    mock_ibm_resp = Mock()
    mock_ibm_resp.status_code = 200
    mock_ibm_resp.json.return_value = ibm_data

    mock_get.side_effect = [mock_aapl_resp, mock_ibm_resp]

    result = get_stock_prices(["AAPL", "IBM"])
    data = json.loads(result)

    assert "stock_prices" in data
    assert len(data["stock_prices"]) == 2


@patch("src.views.os.getenv")
@patch("src.views.time.sleep")
@patch("src.views.requests.get")
def test_get_stock_prices_value_error(mock_get_req: Mock, mock_time_sleep: Mock, mock_getenv: Mock) -> None:
    mock_getenv.return_value = None

    with pytest.raises(ValueError):
        get_stock_prices(["AAPL"])


@patch("src.views.os.getenv")
@patch("src.views.time.sleep")
@patch("src.views.requests.get")
def test_get_stock_prices_value_error_1(mock_get_req: Mock, mock_time_sleep: Mock, mock_getenv: Mock) -> None:
    mock_getenv.return_value = "apy_key"
    result_1 = get_stock_prices([])

    assert result_1 == json.dumps({"stock_prices": []}, indent=4)


@patch("src.views.os.path.dirname")
@patch("src.views.os.path.abspath")
@patch("src.views.open")
def test_load_user_settings_success(mock_open: Mock, mock_abspath: Mock, mock_dirname: Mock) -> None:
    mock_abspath.return_value = "/folder/path/file"
    mock_dirname.side_effect = ["/folder/path", "/folder"]

    raw_data = {"user_currencies": {"USD": 100}, "user_stocks": {"AAPL": 5}}
    json_string = json.dumps(raw_data)

    mock_file = MagicMock()
    mock_file.read.return_value = json_string

    mock_open.return_value.__enter__.return_value = mock_file

    result = load_user_settings("user_settings.json")

    assert result == {"user_currencies": {"USD": 100}, "user_stocks": {"AAPL": 5}}


def test_load_user_settings_error() -> None:
    result = load_user_settings("")

    assert result == {}
