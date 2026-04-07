import pytest
import pandas as pd
from unittest.mock import patch

from src.utils import read_financial_transactions_from_excel


def test_read_financial_transactions_success(create_test_dataframe):

    with patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = create_test_dataframe
        result = read_financial_transactions_from_excel('dummy_path.xlsx')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        assert list(result.columns) == [
            'Дата операции', 'Категория', 'Кэшбэк',
            'Описание', 'Сумма операции с округлением'
        ]
        mock_read_excel.assert_called_once_with('dummy_path.xlsx')


def test_read_financial_transactions_file_not_found():

    with patch('pandas.read_excel', side_effect=FileNotFoundError('Файл не найден')):
        with pytest.raises(FileNotFoundError) as exc_info:
            read_financial_transactions_from_excel('nonexistent.xlsx')
        assert 'Файл не найден' in str(exc_info.value)


def test_read_financial_transactions_value_error():

    with patch('pandas.read_excel', side_effect=ValueError('Некорректный формат Excel')):
        with pytest.raises(ValueError) as exc_info:
            read_financial_transactions_from_excel('corrupted.xlsx')
        assert 'Ошибка формата данных' in str(exc_info.value)


def test_read_financial_transactions_other_exception():

    with patch('pandas.read_excel', side_effect=PermissionError('Нет прав доступа')):
        with pytest.raises(Exception) as exc_info:
            read_financial_transactions_from_excel('restricted.xlsx')
        assert 'Неизвестная ошибка' in str(exc_info.value)
        assert 'Нет прав доступа' in str(exc_info.value)


def test_read_financial_transactions_empty_file(empty_dataframe):

    with patch('pandas.read_excel') as mock_read_excel:
        mock_read_excel.return_value = empty_dataframe
        result = read_financial_transactions_from_excel('empty.xlsx')
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        assert list(result.columns) == [
            'Дата операции', 'Категория', 'Кэшбэк',
            'Описание', 'Сумма операции с округлением'
        ]
