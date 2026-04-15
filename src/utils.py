import json
import logging
import os
import time
from datetime import date, datetime
from typing import Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

API_KEY = os.getenv("API_KEY")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")
PATH_TO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")
PATH_TO_USER_SETTINGS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_settings.json")

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "utils.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def read_financial_transactions_from_excel(path: str) -> pd.DataFrame:
    """Функция, которая принимает на вход путь до Excel-файла и считывает из него финансовые операции"""
    try:
        logger.info(f"Считываем EXCEL файл по указанному пути {path}.")
        transactions = pd.read_excel(path)
        logger.info("Возвращаем объект DataFrame.")
        return transactions
    except FileNotFoundError as ex:
        error_msg = f"Файл не найден: {path}. Ошибка: {ex}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg) from ex
    except ValueError as ex:
        error_msg = f"Ошибка формата данных в файле {path}: {ex}"
        logger.error(error_msg)
        raise ValueError(error_msg) from ex
    except Exception as ex:
        error_msg = f"Неизвестная ошибка при чтении файла {path}: {ex}"
        logger.error(error_msg)
        raise Exception(error_msg) from ex


def load_user_settings() -> Dict[str, List[str]]:
    """Функция, которая загружает пользовательские настройки из файла user_settings.json."""
    try:
        logger.info("Открываем файл с пользовательскими настройками.")
        with open(PATH_TO_USER_SETTINGS, "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.info("Загружаем пользовательские настройки.")
        return settings
    except FileNotFoundError as ex:
        error_msg = f"Файл не найден. Ошибка: {ex}"
        logger.error(error_msg)
        logger.info("Возвращаем настройки по умолчанию.")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}


def get_greeting(input_datetime_str: str) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    input_datetime = datetime.strptime(input_datetime_str, "%Y-%m-%d %H:%M:%S")
    hour = input_datetime.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 17:
        return "Добрый день"
    elif 17 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_exchange_rates(user_currencies: List[str]) -> Dict[str, float]:
    """Функция, которая получает курсы валют к рублю (RUB) через API."""
    rates = {}
    headers = {"apikey": API_KEY}
    for currency in user_currencies:
        try:
            url = "https://api.apilayer.com/exchangerates_data/convert"
            params = {"to": "RUB", "from": currency, "amount": 1}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            if "result" in data:
                rates[currency] = round(data["result"], 2)
            else:
                print(f"Не удалось получить курс для {currency}: ответ API не содержит 'result'")

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса для {currency}: {e}")
        except KeyError as e:
            print(f"Ошибка обработки ответа для {currency}: отсутствует ключ {e}")
        except Exception as e:
            print(f"Неожиданная ошибка для {currency}: {e}")

    return rates


def get_sp500_stocks(user_stocks: List[str]) -> Dict[str, float]:
    """Функция, которая получает стоимость акций через API."""
    stocks_data = {}
    for stock in user_stocks:
        try:
            url = (
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={API_KEY_STOCKS}"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            latest_date = data["Meta Data"]["3. Last Refreshed"]
            price = float(data["Time Series (Daily)"][latest_date]["4. close"])
            stocks_data[stock] = round(price, 2)
            time.sleep(1.5)
        except Exception as e:
            print(f"Ошибка получения данных для акции {stock}: {e}")
            stocks_data[stock] = None
    return stocks_data


def calculate_period(input_datetime: datetime) -> tuple[date, date]:
    """
    Рассчитывает период для анализа: с начала месяца до входной даты.

    Args:
        input_datetime (datetime): Входящая дата и время

    Returns:
        tuple[date, date]: (start_date, end_date) — начало и конец периода
    """
    end_date = input_datetime.date()
    start_date = date(end_date.year, end_date.month, 1)
    return start_date, end_date


if __name__ == "__main__":
    tr_excel = read_financial_transactions_from_excel(PATH_TO_FILE)
    print(tr_excel[:3])
    print(load_user_settings())
    print(get_exchange_rates(["USD", "EUR"]))
    print(get_sp500_stocks(["AAPL", "AMZN"]))
