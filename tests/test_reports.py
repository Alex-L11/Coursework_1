import pandas as pd
import pytest

from src.reports import spending_by_category


def test_spending_by_category_wrong() -> None:
    with pytest.raises(TypeError, match='Данные не формата DataFrame'):
        spending_by_category('not a dataframe', 'Каршеринг')

    with pytest.raises(TypeError, match='Аргумент "category" должен быть строкой'):
        df = pd.DataFrame({"Дата платежа": ["01.01.2024"], "Категория": ["Еда"]})
        spending_by_category(df,123)


def test_spending_by_category_not_columns() -> None:
    df = pd.DataFrame({"Дата": ["01.01.2024"], "Category": ["Еда"]})
    with pytest.raises(ValueError, match='В данных нет нужной колонки'):
        spending_by_category(df, 'Еда')


def test_valid_date_format(spending_by_category_data) -> None:
    result = spending_by_category(spending_by_category_data, "каршеринг", date='01.01.2024')
    assert not result.empty
    assert pd.api.types.is_datetime64_any_dtype(result["Дата платежа"])


def test_no_transaction_for_category(spending_by_category_data) -> None:
    result = spending_by_category(spending_by_category_data, 'Электроника')
    assert result.empty

    expected_cols = ["Дата платежа", "Категория", "Сумма операции с округлением"]
    assert list(result.columns) == expected_cols


