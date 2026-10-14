import pandas as pd
import pytest

from src.reports import spending_by_category, spend_decorator


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


@pytest.mark.parametrize('category', ['Каршеринг'])
def test_spend_decorator_file_default(spending_by_category_data, category, tmp_path):
    file_name = 'spend_report_test.csv'
    test_path = tmp_path / file_name

    @spend_decorator(str(test_path))
    def decorator_func(trans, cat):
        return trans[trans['Категория'] == cat]

    result = decorator_func(spending_by_category_data, category)

    assert test_path.exists(), f'Файл не создан: {test_path}'
    assert test_path.stat().st_size > 0, 'Файл создан, но пустой'

    ex_df = spending_by_category_data[spending_by_category_data['Категория'] == category]
    pd.testing.assert_frame_equal(result.reset_index(drop=True), ex_df.reset_index(drop=True))

