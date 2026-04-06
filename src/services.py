import json
import logging
import os

import pandas as pd

from src.utils import PATH_TO_FILE, read_financial_transactions_from_excel

logger = logging.getLogger("services")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "services.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_most_profitable_cashback(data: str, month: str | int, year: str | int) -> dict | str:
    """
    Функция, которая возвращает JSON-строку с суммой кэшбэка по категориям за указанный месяц и год.

    Возвращает:
        JSON-строку вида {"Категория": сумма}, отсортированную по убыванию сумм.
    """

    try:
        logger.info("Читаем объект DataFrame.")
        df = read_financial_transactions_from_excel(data)

        logger.info("Преобразуем дату.")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        month = int(month)
        year = int(year)
        mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
        filtered_data = df[mask]

        logger.info("Проверяем, что есть данные за указанный период.")
        if filtered_data.empty:
            return json.dumps({"message": "Нет данных за указанный период"}, ensure_ascii=False, indent=2)

        logger.info("Группируем данные по заданным параметрам и находим их сумму.")
        cashback_grouped = filtered_data.groupby("Категория")["Кэшбэк"].sum()
        logger.info("Сортируем по убыванию")
        sum_cashback_sorted = cashback_grouped.sort_values(ascending=False)

        logger.info("Преобразуем сгруппированные и отсортированные данные из файла в формат JSON")
        cashback_data = json.dumps(sum_cashback_sorted.to_dict(), ensure_ascii=False, indent=2)
        return cashback_data

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return json.dumps({"Ошибка данных": str(e)}, ensure_ascii=False, indent=2)


def finds_transfers(data: str, month: str | int, year: str | int) -> dict | str:
    """Функция, возвращает JSON со всеми транзакциями, которые относятся к переводам физлицам
    за указанный месяц и год.

    Возвращает:
        JSON-строку вида {"Описание" (имя и первая буква фамилии с точкой): сумма},
        отсортированную по убыванию сумм."""

    try:
        logger.info("Читаем объект DataFrame.")
        df = read_financial_transactions_from_excel(data)

        logger.info("Преобразуем дату.")
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
        month = int(month)
        year = int(year)
        mask = (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
        filtered_data = df[mask]

        logger.info("Проверяем, что есть данные за указанный период.")
        if filtered_data.empty:
            return json.dumps({"message": "Нет данных за указанный период"}, ensure_ascii=False, indent=2)

        logger.info("Фильтруем данные по заданному критерию.")
        pattern = r"^[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.$"
        is_person = filtered_data["Описание"].astype(str).str.match(pattern)
        person_transfers = filtered_data[is_person]

        logger.info("Проверяем, что есть переводы за указанный период.")
        if person_transfers.empty:
            return json.dumps({"message": "Нет переводов физлицам за указанный период"},
                              ensure_ascii=False, indent=2)

        logger.info("Группируем данные по заданным параметрам и находим их сумму.")
        transfers_grouped = person_transfers.groupby("Описание")["Сумма операции с округлением"].sum()
        logger.info("Сортируем по убыванию")
        sum_transfers_sorted = transfers_grouped.sort_values(ascending=False)

        logger.info("Преобразуем сгруппированные и отсортированные данные из файла в формат JSON")
        transfer_data = json.dumps(sum_transfers_sorted.to_dict(), ensure_ascii=False, indent=2)
        return transfer_data

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return json.dumps({"Ошибка данных": str(e)}, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print(get_most_profitable_cashback(PATH_TO_FILE, "06", "2021"))
    print(finds_transfers(PATH_TO_FILE, "07", "2021"))
