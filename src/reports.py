import json
import pandas as pd
from typing import Optional
from datetime import datetime
from typing import Callable


def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> dict:
    # Если дата не передана, используем текущую дату
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')

    # Преобразовываем строку даты в объект datetime
    end_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = end_date - pd.DateOffset(months=3)  # Получаем дату за 3 месяца

    # Фильтруем транзакции по дате и категории
    mask = (transactions['Дата платежа'] >= start_date) & \
           (transactions['Дата платежа'] <= end_date) & \
           (transactions['Категория'] == category)
    filtered_expenses = transactions.loc[mask]

    # Суммируем затраты
    total_expenses = filtered_expenses['Сумма операции'].sum()

    # Формируем отчет
    report = {
        'Категория': category,
        'Сумма расходов': total_expenses,
        'Операции': filtered_expenses.to_dict(orient='records')
    }

    return report


def report_writer(filename: str = None):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Вызов функции, возвращающей отчет
            report_data = func(*args, **kwargs)

            if filename is None:
                filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Запись в файл
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(report_data, file, ensure_ascii=False, indent=4)

            # Возвращаем исходный отчет
            return report_data

        return wrapper
    return decorator
