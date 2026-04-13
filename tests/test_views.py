from datetime import date

import pandas as pd
import pytest

from src.views import filter_transactions_by_date, get_card_info, get_top_5_transactions


def test_filter_transactions_by_date_empty_result(sample_transactions_df_for_views):
    """Тест фильтрования с пустым результатом."""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)

    result = filter_transactions_by_date(sample_transactions_df_for_views, start_date, end_date)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_filter_transactions_by_date_invalid_date_format():
    """Тест обработки некорректного формата даты."""
    df = pd.DataFrame({'Дата операции': ['некорректная дата']})
    start_date = date(2023, 5, 1)
    end_date = date(2023, 5, 31)

    with pytest.raises(ValueError, match="Не удалось преобразовать колонку 'Дата операции' в формат даты"):
        filter_transactions_by_date(df, start_date, end_date)


def test_get_card_info_success(sample_transactions_df_for_views):
    """Тест успешного получения информации по картам."""
    start_date = date(2023, 5, 1)
    end_date = date(2023, 5, 31)

    result = get_card_info(sample_transactions_df_for_views, start_date, end_date)

    assert isinstance(result, list)
    assert len(result) == 2

    card1 = next(card for card in result if card['last_4_digits'] == '1111')
    assert card1['total_spent'] == -2350  # -1500 + -850
    assert card1['cashback'] == 23.5  # 2350 * 0.01

    card2 = next(card for card in result if card['last_4_digits'] == '4444')
    assert card2['total_spent'] == -3800  # -3200 + -600
    assert card2['cashback'] == 38.0  # 3800 * 0.01


def test_get_card_info_no_transactions_in_period(sample_transactions_df_for_views):
    """Тест получения информации по картам при отсутствии транзакций в периоде."""
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)

    result = get_card_info(sample_transactions_df_for_views, start_date, end_date)

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_card_info_empty_dataframe(empty_transactions_df):
    """Тест получения информации по картам из пустого DataFrame."""
    start_date = date(2023, 5, 1)
    end_date = date(2023, 5, 31)

    result = get_card_info(empty_transactions_df, start_date, end_date)

    assert isinstance(result, list)
    assert len(result) == 0


def test_get_top_5_transactions_success(sample_transactions_df_for_views):
    """Тест успешного получения топ‑5 транзакций."""
    start_date = date(2023, 5, 1)
    end_date = date(2023, 5, 31)

    result = get_top_5_transactions(sample_transactions_df_for_views, start_date, end_date)

    assert isinstance(result, list)
    assert len(result) == 4
    assert result[0]['amount'] == -3200
    assert result[-1]['amount'] == -600

    for transaction in result:
        assert isinstance(transaction['date'], str)
        assert len(transaction['date']) == 10
