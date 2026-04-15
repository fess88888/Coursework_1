from datetime import date, datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
import requests

from src.utils import (calculate_period, get_exchange_rates, get_greeting, get_sp500_stocks, load_user_settings,
                       read_financial_transactions_from_excel)


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


def test_load_user_settings_success():
    """Тест успешной загрузки настроек из файла."""
    mock_file_data = '{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}'

    with patch('src.utils.logger') as mock_logger, \
         patch('builtins.open', mock_open(read_data=mock_file_data)):

        result = load_user_settings()

        assert result == {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
        mock_logger.info.assert_any_call("Открываем файл с пользовательскими настройками.")
        mock_logger.info.assert_any_call("Загружаем пользовательские настройки.")


def test_load_user_settings_file_not_found():
    """Тест обработки ошибки отсутствия файла настроек."""
    with patch('src.utils.logger') as mock_logger, \
         patch('builtins.open', side_effect=FileNotFoundError):

        result = load_user_settings()
        expected_default = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        }
        assert result == expected_default
        mock_logger.error.assert_called()


def test_get_greeting_morning():
    """Тест приветствия для утреннего времени."""
    result = get_greeting("2021-05-20 08:30:00")
    assert result == "Доброе утро"


def test_get_greeting_afternoon():
    """Тест приветствия для дневного времени."""
    result = get_greeting("2021-05-20 14:30:00")
    assert result == "Добрый день"


def test_get_greeting_evening():
    """Тест приветствия для вечернего времени."""
    result = get_greeting("2021-05-20 19:30:00")
    assert result == "Добрый вечер"


def test_get_greeting_night():
    """Тест приветствия для ночного времени."""
    result = get_greeting("2021-05-20 01:30:00")
    assert result == "Доброй ночи"


def test_get_exchange_rates_success():
    """Тест успешного получения курсов валют."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"result": 75.5}

    with patch('src.utils.requests.get', return_value=mock_response):
        result = get_exchange_rates(["USD"])
        assert "USD" in result
        assert result["USD"] == 75.5


def test_get_exchange_rates_request_exception():
    """Тест обработки ошибок запроса к API курсов валют."""
    with patch('src.utils.requests.get', side_effect=requests.exceptions.RequestException("Connection error")):
        result = get_exchange_rates(["USD"])
        assert result == {}


def test_get_sp500_stocks_success():
    """Тест успешного получения цен акций."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "Meta Data": {"3. Last Refreshed": "2021-05-20"},
        "Time Series (Daily)": {"2021-05-20": {"4. close": "150.75"}}
    }

    with patch('src.utils.requests.get', return_value=mock_response):
        result = get_sp500_stocks(["AAPL"])
        assert "AAPL" in result
        assert result["AAPL"] == 150.75


def test_get_sp500_stocks_exception():
    """Тест обработки ошибок API для акций."""
    with patch('src.utils.requests.get', side_effect=Exception("API error")):
        result = get_sp500_stocks(["AAPL"])
        assert "AAPL" in result
        assert result["AAPL"] is None


def test_calculate_period():
    """Тест расчёта периода (с начала месяца до входной даты)."""
    input_datetime = datetime(2021, 5, 20, 13, 57, 21)
    start_date, end_date = calculate_period(input_datetime)

    assert start_date == date(2021, 5, 1)
    assert end_date == date(2021, 5, 20)


def test_get_exchange_rates_key_error():
    """Тест обработки KeyError"""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.side_effect = KeyError("result")

    with patch('src.utils.requests.get', return_value=mock_response):
        result = get_exchange_rates(["USD"])
        assert "USD" not in result


def test_get_exchange_rates_unexpected_exception():
    """Тест обработки неожиданных исключений."""
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Unexpected error")

    with patch('src.utils.requests.get', return_value=mock_response):
        result = get_exchange_rates(["USD"])
        assert "USD" not in result


def test_get_exchange_rates_no_result_in_response():
    """Тест обработки ответа API без ключа 'result'."""
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"success": False, "error": "Invalid parameters"}

    with patch('src.utils.requests.get', return_value=mock_response):
        result = get_exchange_rates(["USD"])
        assert "USD" not in result
