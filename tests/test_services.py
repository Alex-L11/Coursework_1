import json
import pytest
import pandas as pd
from unittest.mock import Mock, patch
from src.services import category_cashback


def test_category_cashback_type_error() -> None:
        with pytest.raises(TypeError):
            category_cashback('operations.xlsx', 'str', 4.5)



@patch('src.services.read_excel')
def test_category_cashback_success(mock_read_excel, data_frame_for_category_cashback) -> None:
    mock_read_excel.return_value = data_frame_for_category_cashback
    result_json = category_cashback('excel', 2023, 1)
    result = json.loads(result_json)
    assert result == {'Досуг': 5, 'Продукты': 1, 'Транспорт': 2}


