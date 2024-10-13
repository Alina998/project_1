import unittest
import json
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

from src.reports import spending_by_category, report_writer


# Тестируем функцию сортировки по категории
class TestSpendingByCategory(unittest.TestCase):

    def setUp(self):
        # Создаем тестовый DataFrame
        data = {
            'Дата платежа': [
                '2021-12-31',  # Транзакция 1
                '2021-12-31',  # Транзакция 2
                '2022-01-15',  # Транзакция 3 (должна быть в выборке)
                '2022-10-01'  # Транзакция 4 (должна быть за пределами выборки)
            ],
            'Номер карты': ['*7197', '*7197', '*1234', '*5678'],
            'Статус': ['OK', 'OK', 'OK', 'OK'],
            'Сумма операции': [-160.89, -64.00, -100.00, -50.00],
            'Валюта операции': ['RUB', 'RUB', 'RUB', 'RUB'],
            'Сумма платежа': [-160.89, -64.00, -100.00, -50.00],
            'Валюта платежа': ['RUB', 'RUB', 'RUB', 'RUB'],
            'Кэшбэк': [0.00, 0.00, 0.00, 0.00],
            'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Еда'],
            'MCC': [5411, 5411, 5411, 5812],
            'Описание': ['Колхоз', 'Колхоз', 'Колхоз', 'Ресторан'],
            'Бонусы (включая кэшбэк)': [3.00, 1.00, 0.00, 0.00],
            'Округление на инвесткопилку': [0.00, 0.00, 0.00, 0.00],
            'Сумма операции с округлением': [160.89, 64.00, 100.00, 50.00],
        }

        self.transactions_df = pd.DataFrame(data)
        self.transactions_df['Дата платежа'] = pd.to_datetime(self.transactions_df['Дата платежа'])

    def test_spending_by_category_within_date_range(self):
        category = 'Супермаркеты'

        # Проверяем,все операции в пределах 3 месяцев
        today = datetime.now()
        expected_total = -224.89  # -160.89 + -64.00
        result = spending_by_category(self.transactions_df, category, today.strftime('%Y-%m-%d'))

        self.assertEqual(result['Категория'], category)
        self.assertEqual(result['Сумма расходов'], expected_total)
        self.assertEqual(len(result['Операции']), 2)  # Должно быть 2 операции

    def test_spending_by_category_no_transactions(self):
        category = 'Еда'  # Не имеем никаких данных

        # Создаем тестовый DataFrame с одной транзакцией в другой категории
        empty_data = {
            'Дата платежа': [],
            'Номер карты': [],
            'Статус': [],
            'Сумма операции': [],
            'Валюта операции': [],
            'Сумма платежа': [],
            'Валюта платежа': [],
            'Кэшбэк': [],
            'Категория': [],
            'MCC': [],
            'Описание': [],
            'Бонусы (включая кэшбэк)': [],
            'Округление на инвесткопилку': [],
            'Сумма операции с округлением': [],
        }

        empty_df = pd.DataFrame(empty_data)
        result = spending_by_category(empty_df, category)

        self.assertEqual(result['Категория'], category)
        self.assertEqual(result['Сумма расходов'], 0)
        self.assertEqual(len(result['Операции']), 0)

    def test_spending_by_category_with_date(self):
        category = 'Супермаркеты'
        # Устанавливаем дату 45 дней назад
        date = (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d')
        expected_total = -160.89  # Одна операция за последние 45 дней
        result = spending_by_category(self.transactions_df, category, date)

        self.assertEqual(result['Категория'], category)
        self.assertEqual(result['Сумма расходов'], expected_total)

    def test_spending_by_category_empty_dataframe(self):
        empty_transactions = pd.DataFrame(columns=[
            'Дата платежа', 'Номер карты', 'Статус', 'Сумма операции',
            'Валюта операции', 'Сумма платежа', 'Валюта платежа',
            'Кэшбэк', 'Категория', 'MCC', 'Описание',
            'Бонусы (включая кэшбэк)', 'Округление на инвесткопилку',
            'Сумма операции с округлением'
        ])
        category = 'Супермаркеты'
        result = spending_by_category(empty_transactions, category)

        self.assertEqual(result['Категория'], category)
        self.assertEqual(result['Сумма расходов'], 0)
        self.assertEqual(len(result['Операции']), 0)


# Тестируем декоратор, формирующий отчет
class TestReportWriter(unittest.TestCase):
    def setUp(self):
        # Создаем тестовый DataFrame
        data = {
            'Дата платежа': [
                '2021-12-31',  # Транзакция 1
                '2021-12-31',  # Транзакция 2
                '2022-01-15',  # Транзакция 3 (должна быть в выборке)
                '2022-10-01'  # Транзакция 4 (должна быть за пределами выборки)
            ],
            'Номер карты': ['*7197', '*7197', '*1234', '*5678'],
            'Статус': ['OK', 'OK', 'OK', 'OK'],
            'Сумма операции': [-160.89, -64.00, -100.00, -50.00],
            'Валюта операции': ['RUB', 'RUB', 'RUB', 'RUB'],
            'Сумма платежа': [-160.89, -64.00, -100.00, -50.00],
            'Валюта платежа': ['RUB', 'RUB', 'RUB', 'RUB'],
            'Кэшбэк': [0.00, 0.00, 0.00, 0.00],
            'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты', 'Еда'],
            'MCC': [5411, 5411, 5411, 5812],
            'Описание': ['Колхоз', 'Колхоз', 'Колхоз', 'Ресторан'],
            'Бонусы (включая кэшбэк)': [3.00, 1.00, 0.00, 0.00],
            'Округление на инвесткопилку': [0.00, 0.00, 0.00, 0.00],
            'Сумма операции с округлением': [160.89, 64.00, 100.00, 50.00],
        }
        self.transactions_df = pd.DataFrame(data)
        self.transactions_df['Дата платежа'] = pd.to_datetime(self.transactions_df['Дата платежа'])

    @patch("builtins.open", new_callable=mock_open)
    def test_report_writer_default_filename(self, mock_open):
        @report_writer()
        def generate_report(transactions, category):
            return spending_by_category(transactions, category)

        report = generate_report(self.transactions_df, 'Супермаркеты')

        # Проверяем, что файл открыт с именем по умолчанию
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        mock_open.assert_called_once_with(filename, 'w', encoding='utf-8')

        # Проверяем, что данные были записаны в файл
        expected_data = json.dumps(report, ensure_ascii=False, indent=4)
        mock_open().write.assert_called_once_with(expected_data)

    @patch("builtins.open", new_callable=mock_open)
    def test_report_writer_custom_filename(self, mock_open):
        @report_writer(filename="custom_report.json")
        def generate_report(transactions, category):
            return spending_by_category(transactions, category)

        report = generate_report(self.transactions_df, 'Супермаркеты')

        # Проверяем, что файл открыт с переданным именем
        mock_open.assert_called_once_with("custom_report.json", 'w', encoding='utf-8')

        # Проверяем, что данные были записаны в файл
        expected_data = json.dumps(report, ensure_ascii=False, indent=4)
        mock_open().write.assert_called_once_with(expected_data)


if __name__ == '__main__':
    unittest.main()
