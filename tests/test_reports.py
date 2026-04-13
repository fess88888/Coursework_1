from unittest import mock

import pytest
import pandas as pd
from datetime import datetime
from unittest.mock import patch

from src.reports import spending_by_weekday, WEEKDAY_NAMES


@pytest.mark.parametrize("input_date,expected_days_count", [
    (datetime(2021, 12, 31), 7),  # Все дни недели представлены
    (datetime(2021, 1, 1), 0),   # Нет данных за период
])
def test_spending_by_weekday_with_different_dates(sample_transactions_df, input_date, expected_days_count):
    """Тест с разными датами отсчёта."""
    result = spending_by_weekday(sample_transactions_df, input_date)
    assert isinstance(result, dict)
    assert len(result) == 7  # Всегда 7 дней недели

    if expected_days_count == 0:
        # Если нет данных, все значения должны быть 0.0
        assert all(value == 0.0 for value in result.values())
    else:
        # Проверяем, что есть хотя бы одно ненулевое значение
        assert any(value > 0 for value in result.values())


@patch('src.reports.logger')
def test_logging_calls(mock_logger, sample_transactions_df):
    """Тест вызовов логирования."""
    spending_by_weekday(sample_transactions_df, datetime(2021, 12, 31))

    # Проверяем основные вызовы логирования
    assert mock_logger.info.call_count >= 4  # Минимум 4 инфо-сообщения
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


@patch('json.dump')
@patch('os.makedirs')
def test_decorator_functionality(mock_makedirs, mock_json_dump, sample_transactions_df):
    """Тест функциональности декоратора."""
    result = spending_by_weekday(sample_transactions_df, datetime(2021, 12, 31))

    mock_makedirs.assert_called_once()
    mock_json_dump.assert_called_once_with(
        result,
        mock.ANY,  # file object
        ensure_ascii=False,
        indent=4
    )


@pytest.mark.parametrize("weekday_num,expected_day_name", [
    (0, 'Понедельник'),
    (1, 'Вторник'),
    (2, 'Среда'),
    (3, 'Четверг'),
    (4, 'Пятница'),
    (5, 'Суббота'),
    (6, 'Воскресенье'),
])
def test_weekday_names_mapping(weekday_num, expected_day_name):
    """Параметризованный тест сопоставления номеров дней и названий."""
    assert WEEKDAY_NAMES[weekday_num] == expected_day_name


def test_average_calculation_accuracy(sample_transactions_df):
    """Тест точности расчёта средних значений."""
    test_data = {
        'Дата операции': [
            '01.12.2021 10:00:00',
            '08.12.2021 11:00:00',
            '15.12.2021 12:00:00',
        ],
        'Сумма операции с округлением': [30.0, 60.0, 90.0]  # Среднее = 60.0
    }
    test_df = pd.DataFrame(test_data)
    result = spending_by_weekday(test_df, datetime(2021, 12, 31))
    # Среднее для среды должно быть 60.0
    assert result['Среда'] == 60.0


def test_specific_exception_types_are_rethrown_correctly():
    """Тест разные типы исключений."""
    test_cases = [
        (ValueError("Проблема с данными"), ValueError),
        (TypeError("Неверный тип данных"), TypeError),
        (KeyError("Отсутствует колонка"), KeyError),
        (AttributeError("Нет атрибута"), AttributeError)
    ]

    sample_df = pd.DataFrame({
        'Дата операции': ['01.12.2021 10:00:00'],
        'Сумма операции с округлением': [100.0]
    })

    for exception, expected_type in test_cases:
        with patch('pandas.DataFrame.copy', side_effect=exception):
            with pytest.raises(expected_type) as exc_info:
                spending_by_weekday(sample_df, datetime(2021, 12, 31))
            assert isinstance(exc_info.value, expected_type)
            assert str(exception) in str(exc_info.value)


def test_uses_current_date_when_none_provided():
    """Тест функция использует текущую дату."""
    sample_df = pd.DataFrame({
        'Дата операции': ['01.12.2021 10:00:00', '02.12.2021 11:00:00'],
        'Сумма операции с округлением': [100.0, 200.0]
    })

    with patch('src.reports.datetime') as mock_datetime:
        mock_now = datetime(2021, 12, 31, 15, 30, 0)
        mock_datetime.now.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
        spending_by_weekday(sample_df)
        assert mock_datetime.now.called
