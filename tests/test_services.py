import json
from unittest.mock import patch

from src.services import finds_transfers, get_most_profitable_cashback


def test_get_most_profitable_cashback_success(create_test_dataframe):

    with patch("src.services.read_financial_transactions_from_excel") as mock_read:
        mock_read.return_value = create_test_dataframe
        result = get_most_profitable_cashback("dummy_path", "06", "2021")
        data = json.loads(result)
        assert "Продукты" in data
        assert data["Продукты"] == 100
        assert data["Развлечения"] == 50


def test_finds_transfers_success(create_test_dataframe):

    with patch("src.services.read_financial_transactions_from_excel") as mock_read:
        mock_read.return_value = create_test_dataframe
        result = finds_transfers("dummy_path", "07", "2021")
        data = json.loads(result)
        assert "Петр П." in data
        assert data["Петр П."] == 1500


def test_get_most_profitable_cashback_no_data(empty_dataframe):

    with patch("src.services.read_financial_transactions_from_excel") as mock_read:
        mock_read.return_value = empty_dataframe
        result = get_most_profitable_cashback("dummy_path", "13", "2021")
        data = json.loads(result)
        assert "message" in data
        assert data["message"] == "Нет данных за указанный период"


def test_finds_transfers_no_person_transfers(create_test_dataframe):

    with patch("src.services.read_financial_transactions_from_excel") as mock_read:
        df = create_test_dataframe.copy()
        df["Описание"] = ["Магазин", "Аптека", "Кафе", "Ресторан"]
        mock_read.return_value = df
        result = finds_transfers("dummy_path", "07", "2021")
        data = json.loads(result)
        assert "message" in data
        assert data["message"] == "Нет переводов физлицам за указанный период"


def test_finds_transfers_no_data_period(empty_dataframe):

    with patch("src.services.read_financial_transactions_from_excel") as mock_read:
        mock_read.return_value = empty_dataframe
        result = finds_transfers("dummy_path", "07", "2021")
        data = json.loads(result)
        assert "message" in data
        assert data["message"] == "Нет данных за указанный период"


def test_get_most_profitable_cashback_file_error():

    with patch("src.services.read_financial_transactions_from_excel", side_effect=Exception("Файл не найден")):
        result = get_most_profitable_cashback("invalid_path", "06", "2021")
        data = json.loads(result)
        assert "Ошибка данных" in data
        assert "Файл не найден" in data["Ошибка данных"]


def test_finds_transfers_file_error():

    with patch("src.services.read_financial_transactions_from_excel", side_effect=Exception("Ошибка доступа к файлу")):
        result = finds_transfers("invalid_path", "07", "2021")
        data = json.loads(result)
        assert "Ошибка данных" in data
        assert "Ошибка доступа к файлу" in data["Ошибка данных"]
