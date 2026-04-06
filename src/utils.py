import logging
import os

import pandas as pd

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "utils.log"), "w", encoding="utf-8"
)
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

PATH_TO_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")


def read_financial_transactions_from_excel(path: str) -> pd.DataFrame:
    """Функция, которая принимает на вход путь до Excel-файла и считывает из него финансовые операции"""
    try:
        logger.info(f"Считываем EXCEL файл по указанному пути {path}.")
        transactions = pd.read_excel(path)
        logger.info("Возвращаем объект DataFrame.")
        return transactions
    except (FileNotFoundError, ValueError) as ex:
        logger.error(f"Произошла ошибка: {ex}")


if __name__ == "__main__":
    tr_excel = read_financial_transactions_from_excel(PATH_TO_FILE)
    print(tr_excel[:3])
