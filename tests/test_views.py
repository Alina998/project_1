import unittest
from unittest.mock import patch
from flask import json
from src.views import app
import pandas as pd


class TestFinancialAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.load_user_settings')
    @patch('app.get_currency_data')
    @patch('app.get_stock_data')
    @patch('pandas.read_excel')
    def test_get_events(self, mock_read_excel, mock_get_stock_data, mock_get_currency_data, mock_load_user_settings):
        # Mock data
        mock_operations_data = pd.DataFrame({
            'Дата': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'Категория': ['Еда', 'Транспорт', 'Наличные'],
            'Сумма операции': [-100, -50, -30]
        })
        mock_read_excel.return_value = mock_operations_data

        mock_load_user_settings.return_value = {
            'user_currencies': ['USD', 'EUR'],
            'user_stocks': ['AAPL', 'GOOGL']
        }
        mock_get_currency_data.return_value = {'USD': 74.5, 'EUR': 88.0}
        mock_get_stock_data.return_value = {'AAPL': 150.0, 'GOOGL': 2800.0}

        data = json.loads(response.data)

        # Проверка расходов
        self.assertIn('Расходы', data)
        self.assertEqual(data['Расходы']['Общая сумма'], 180)
        self.assertIn('Основные', data['Расходы'])
        self.assertIn('Переводы и наличные', data['Расходы'])

        # Проверка поступлений
        self.assertIn('Поступления', data)
        self.assertEqual(data['Поступления']['Общая сумма'], 0)

        # Проверка курса
        self.assertIn('Курс валют', data)
        self.assertEqual(data['Курс валют'], {'USD': 74.5, 'EUR': 88.0})

        # Проверка акций
        self.assertIn('Стоимость акций', data)
        self.assertEqual(data['Стоимость акций'], {'AAPL': 150.0, 'GOOGL': 2800.0})


if __name__ == '__main__':
    unittest.main()
