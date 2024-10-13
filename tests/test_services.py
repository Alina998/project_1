import unittest
import pandas as pd
from src.services import search_transactions


class TestSearchTransactions(unittest.TestCase):

    def setUp(self):
        # Создаем тестовый DataFrame
        data = {
            'Сумма операции': [-160.89, -64.00, -118.12, -78.05, -564.00],
            'Валюта операции': ['RUB'] * 5,
            'Сумма платежа': [-160.89, -64.00, -118.12, -78.05, -564.00],
            'Валюта платежа': ['RUB'] * 5,
            'Кэшбэк': [3.00, 1.00, 2.00, 1.00, 5.00],
            'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Различные товары'],
            'MCC': [5411, 5411, 5411, 5411, 5399],
            'Описание': ['Колхоз', 'Колхоз', 'Магнит', 'Колхоз', 'Ozon.ru'],
            'Бонусы (включая кэшбэк)': [3.00, 1.00, 2.00, 1.00, 5.00],
            'Округление на инвесткопилку': [0.00] * 5,
            'Сумма операции с округлением': [160.89, 64.00, 118.12, 78.05, 564.00],
        }
        self.transactions_df = pd.DataFrame(data)

    def test_search_by_description(self):
        result = search_transactions(self.transactions_df, "Колхоз")
        self.assertEqual(len(result), 3)  # Должны найти 3 транзакции

    def test_search_by_category(self):
        result = search_transactions(self.transactions_df, "Супермаркеты")
        self.assertEqual(len(result), 4)  # Должны найти 4 транзакции

    def test_search_by_notifyussch(self):
        result = search_transactions(self.transactions_df, "Ozon.ru")
        self.assertEqual(len(result), 1)  # Должны найти 1 транзакцию

    def test_search_by_invalid_string(self):
        result = search_transactions(self.transactions_df, "Неизвестный")
        self.assertEqual(len(result), 0)  # Ничего не должно быть найдено

    def test_search_case_insensitive(self):
        result = search_transactions(self.transactions_df, "колхоз")
        self.assertEqual(len(result), 3)  # Должны найти 3 транзакции (не чувствительно к регистру)

    def test_search_by_numeric_value(self):
        result = search_transactions(self.transactions_df, "-160.89")
        self.assertEqual(len(result), 1)  # Должны найти 1 транзакцию по сумме операции


if __name__ == '__main__':
    unittest.main()
