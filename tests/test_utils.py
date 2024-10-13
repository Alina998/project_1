import unittest
from unittest.mock import patch, mock_open
import json
from src.utils import load_user_settings, get_date, get_currency_data, get_stock_data, generate_json_response
from unittest.mock import MagicMock


class TestFinanceFunctions(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}')
    def test_load_user_settings(self, mock_file):
        settings = load_user_settings('user_settings.json')
        expected = {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "GOOGL"]
        }
        self.assertEqual(settings, expected)

    def test_get_date(self):
        start_date, end_date = get_date("20.05.2020")
        self.assertEqual(start_date, "2020-05-01")
        self.assertEqual(end_date, "2020-05-20")

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_currency_data_success(self, mock_getenv, mock_get):
        # Настройка
        mock_getenv.return_value = 'mock_api_key'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'rates': {'USD': 1.2, 'EUR': 0.9}}
        mock_get.return_value = mock_response

        # Вызов тестируемой функции
        result = get_currency_data('01.01.2023', ['USD', 'EUR'])

        # Проверка результатов
        self.assertEqual(result['USD'], {'rates': {'USD': 1.2, 'EUR': 0.9}})
        self.assertEqual(result['EUR'], {'rates': {'USD': 1.2, 'EUR': 0.9}})
        mock_get.assert_called()

    @patch('requests.get')
    @patch('os.getenv')
    def test_get_currency_data_failure(self, mock_getenv, mock_get):
        # Настройка
        mock_getenv.return_value = 'mock_api_key'
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        # Вызов тестируемой функции
        result = get_currency_data('01.01.2023', ['USD', 'EUR'])

        # Проверка результатов
        self.assertEqual(result['USD'], {'error': 'Не удалось получить данные'})
        self.assertEqual(result['EUR'], {'error': 'Не удалось получить данные'})
        mock_get.assert_called()

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_get_stock_data(self, mock_get, mock_get_env):
        mock_response = {
            "Time Series (Daily)": {
                "2020-05-20": {
                    "1. open": "100.0",
                    "2. high": "110.0",
                    "3. low": "90.0",
                    "4. close": "105.0",
                    "5. volume": "10000"
                }
            }
        }

        # Создаем объект подобный отдаче requests
        mock_get.return_value = unittest.mock.Mock()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        # Вызов функции
        data = get_stock_data(["AAPL", "GOOGL"])

        # Проверяем, что данные получены
        self.assertIn("AAPL", data)
        self.assertIn("GOOGL", data)

    def test_generate_json_response(self):
        data = {"key": "value"}
        json_response = generate_json_response(data)
        self.assertEqual(json.loads(json_response), data)


if __name__ == "__main__":
    unittest.main()
