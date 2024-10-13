import pandas as pd


def search_transactions(transactions_df: pd.DataFrame, search_string: str) -> pd.DataFrame:
    # Приводим искомую строку к нижнему регистру для нечувствительности к регистру
    search_string = search_string.lower()

    # Фильтруем DataFrame по всем нужным столбцам
    mask = (
            transactions_df['Описание'].str.contains(search_string, case=False) |
            transactions_df['Категория'].str.contains(search_string, case=False) |
            transactions_df['Сумма операции'].astype(str).str.contains(search_string) |
            transactions_df['Валюта операции'].str.contains(search_string) |
            transactions_df['Сумма платежа'].astype(str).str.contains(search_string) |
            transactions_df['Валюта платежа'].str.contains(search_string) |
            transactions_df['Кэшбэк'].astype(str).str.contains(search_string) |
            transactions_df['MCC'].astype(str).str.contains(search_string) |
            transactions_df['Бонусы (включая кэшбэк)'].astype(str).str.contains(search_string) |
            transactions_df['Округление на инвесткопилку'].astype(str).str.contains(search_string) |
            transactions_df['Сумма операции с округлением'].astype(str).str.contains(search_string)
    )

    # Возвращаем отфильтрованный DataFrame
    return transactions_df[mask]
