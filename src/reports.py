import json
import os
from functools import wraps

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Callable, Any

from src.utils import read_financial_transactions_from_excel, PATH_TO_FILE

logger = logging.getLogger("reports")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "reports.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

WEEKDAY_NAMES = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье'
}


def report_result(filename: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            return result
        return wrapper
    return decorator


@report_result("logs/spending_report.json")
def spending_by_weekday(
    transactions_df: pd.DataFrame,
    date: Optional[datetime] = None
) -> Dict[str, float]:
    """
    Функция, которая рассчитывает средние траты в каждый из дней недели за последние три месяца.
    """
    try:
        transactions_df['Дата операции'] = pd.to_datetime(transactions_df['Дата операции'], format='%d.%m.%Y %H:%M:%S')

        if date is None:
            reference_date = datetime.now()
            logger.info("Используется текущая дата как дата отсчёта")
        else:
            reference_date = date
            logger.info(f"Используется указанная дата как дата отсчёта: {reference_date}")

        logger.info("Рассчитываем дату начала периода (3 месяца назад)")
        start_date = reference_date - timedelta(days=90)
        logger.info(f"Период анализа: с {start_date.date()} по {reference_date.date()}")

        logger.info("Фильтруем транзакции за последние 3 месяца")
        filtered_df = transactions_df[
            (transactions_df["Дата операции"] >= start_date) &
            (transactions_df["Дата операции"] <= reference_date)
        ].copy()

        if filtered_df.empty:
            logger.warning("Нет транзакций за указанный период")
            return {day_name: 0.0 for day_name in WEEKDAY_NAMES.values()}

        logger.info("Добавляем колонку с днём недели (0=понедельник, 6=воскресенье)")
        filtered_df['День недели'] = filtered_df["Дата операции"].dt.dayofweek

        logger.info("Группируем по дням недели и рассчитываем среднее")
        weekly_avg = filtered_df.groupby('День недели')['Сумма операции с округлением'].mean().round(2)

        logger.info("Преобразуем номера дней в текстовые обозначения")
        result = {}
        for day_num in range(7):
            day_name = WEEKDAY_NAMES[day_num]
            if day_num in weekly_avg.index:
                result[day_name] = float(weekly_avg[day_num])
            else:
                result[day_name] = 0.0

        logger.info("Выводим результат")
        return result

    except Exception as e:
        logger.error(f"Ошибка при расчёте: {e}")
        raise


if __name__ == '__main__':
    test_df = read_financial_transactions_from_excel(PATH_TO_FILE)
    our_date = datetime(2021, 12, 31)
    print(spending_by_weekday(test_df, our_date))
