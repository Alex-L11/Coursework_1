import os
import pandas as pd
import json

from typing import Any, Hashable


def get_fin_oper_xlsx(data_xlsx: str) -> list[dict[Hashable, Any]]:
    """ Принимает путь к файлу Excel и выдает список словарей с транзакциями. """
    # папка где лежит проект
    base_dir = os.path.dirname(__file__)

    # поднимаемся в корень проекта
    project_root = os.path.dirname(base_dir)

    # собираем путь до файла целиком
    data_path = os.path.join(project_root, 'data', data_xlsx)
    if not os.path.exists(data_path):
        raise FileNotFoundError(f'Файл не найден: {data_xlsx}')
    try:
        trans_xlsx = pd.read_excel(data_path)
        result = trans_xlsx.to_dict(orient='records')
        return result
    except ValueError:
        raise ValueError('Файл пустой или содержит некорректные данные')
