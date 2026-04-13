import json
from datetime import datetime

import pandas as pd

from src.utils import (PATH_TO_FILE, calculate_period, get_exchange_rates, get_greeting, get_sp500_stocks,
                       load_user_settings, read_financial_transactions_from_excel)
from src.views import get_card_info, get_top_5_transactions


def main_report(input_datetime_str: str, transactions_df: pd.DataFrame) -> str:
    """
    Главная функция, принимающая строку с датой и временем и возвращающая JSON‑ответ.
    """
    # Получаем входную дату
    input_datetime = datetime.strptime(input_datetime_str, "%Y-%m-%d %H:%M:%S")

    # Рассчитываем период: с начала месяца до входной даты
    start_date, end_date = calculate_period(input_datetime)

    # Получаем приветствие
    greeting = get_greeting(input_datetime_str)

    # Получаем данные по картам
    cards_info = get_card_info(transactions_df, start_date, end_date)

    # Получаем топ‑5 транзакций
    top_transactions = get_top_5_transactions(transactions_df, start_date, end_date)

    # Загружаем пользовательские настройки
    user_settings = load_user_settings()
    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    # Получаем курсы валют
    currency_rates = get_exchange_rates(user_currencies)

    # Получаем цены акций
    stock_prices = get_sp500_stocks(user_stocks)

    # Формируем итоговый JSON
    report = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(report, ensure_ascii=False, indent=2)


# Пример использования
if __name__ == "__main__":
    uses_transactions = read_financial_transactions_from_excel(PATH_TO_FILE)
    input_date_time = "2021-12-13 13:57:21"
    json_result = main_report(input_date_time, uses_transactions)
    print(json_result)
