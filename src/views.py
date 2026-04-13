import logging
import os
from datetime import date
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger("views")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "views.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def filter_transactions_by_date(transactions: pd.DataFrame, start_date: date, end_date: date) -> pd.DataFrame:
    """Функция, которая фильтрует транзакции по диапазону дат."""
    df = transactions.copy()

    logger.info("Преобразуем колонку 'Дата операции' в datetime с обработкой ошибок")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce")

    logger.info("Проверяем, что преобразование прошло успешно")
    if df["Дата операции"].isna().all():
        raise ValueError("Не удалось преобразовать колонку 'Дата операции' в формат даты. Проверьте данные.")

    logger.info("Извлекаем дату из datetime")
    df["Дата операции"] = df["Дата операции"].dt.date

    logger.info("Фильтруем по диапазону дат")
    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date) & (df["Дата операции"].notna())
    return df[mask]


def get_card_info(transactions_df: pd.DataFrame, start_date: date, end_date: date) -> List[Dict]:
    """
    Функция, которая получает информацию по картам из DataFrame с транзакциями и
    возвращает список словарей с информацией по каждой карте.
    """
    logger.info("Фильтруем транзакции по дате")
    transactions_df["Дата операции"] = pd.to_datetime(transactions_df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    mask = (transactions_df["Дата операции"].dt.date >= start_date) & (
        transactions_df["Дата операции"].dt.date <= end_date
    )
    filtered_transactions = transactions_df[mask]

    logger.info("Группируем по номеру карты")
    card_groups = filtered_transactions.groupby("Номер карты")

    cards_info = []
    for card_number, group in card_groups:
        logger.info("Получаем последние 4 цифры номера карты")
        last_4_digits = card_number[-4:]

        logger.info("Получаем общую сумму расходов")
        total_spent = group[group["Сумма операции"] < 0]["Сумма операции"].sum()

        logger.info("Считаем кэшбэк (1 % от расходов)")
        cashback = abs(total_spent) * 0.01

        cards_info.append(
            {"last_4_digits": last_4_digits, "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)}
        )

    return cards_info


def get_top_5_transactions(all_transactions: pd.DataFrame, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """Функция, которая возвращает топ‑5 транзакций по сумме платежа за период."""
    filtered_transactions = filter_transactions_by_date(all_transactions, start_date, end_date)

    logger.info("Сортируем по модулю суммы")
    sorted_transactions = filtered_transactions.assign(
        abs_amount=filtered_transactions["Сумма операции"].abs()
    ).sort_values("abs_amount", ascending=False)

    logger.info("Берём топ‑5 и преобразуем в список словарей")
    top_5 = sorted_transactions.head(5)

    result = []
    for _, row in top_5.iterrows():
        result.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": round(float(row["Сумма операции"]), 2),
                "category": row.get("Категория", ""),
                "description": row.get("Описание", ""),
            }
        )
    return result
