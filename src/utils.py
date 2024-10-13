import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# Веб-страницы


def load_user_settings(file_path='user_settings.json'):
    with open(file_path, 'r') as file:
        return json.load(file)


def get_date(input_date_str):
    input_date = datetime.strptime(input_date_str, '%d.%m.%Y')

    # Определение начала месяца
    start_date = input_date.replace(day=1).strftime('%Y-%m-%d')
    end_date = input_date.strftime('%Y-%m-%d')
    return start_date, end_date


def get_currency_data(input_date_str, currencies):
    start_date, end_date = get_date(input_date_str)


    base_currency = currencies[0]
    data = {}
    for currency in currencies:
        api_key_1 = os.getenv('API_KEY_1')
        url = f"https://api.exchangeratesapi.io/v1/history?start_at={start_date}&end_at={end_date}&base={base_currency}&symbols={currency}&access_key={api_key_1}"
        response = requests.get(url)
        if response.status_code == 200:
            data[currency] = response.json()
        else:
            data[currency] = {'error': 'Не удалось получить данные'}

    return data


def get_stock_data(stocks):
    stock_data = {}
    for stock in stocks:
        api_key_2 = os.getenv('API_KEY_2')
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&apikey={api_key_2}"
        response = requests.get(url)
        if response.status_code == 200:
            stock_data[stock] = response.json()
        else:
            stock_data[stock] = {'error': 'Unable to fetch data'}


    return stock_data


def generate_json_response(data):
    return json.dumps(data)


def main():
    # Веб-страницы
    settings = load_user_settings('C:/Users/pasta/Desktop/project_1_bank/user_settings.json')
    currency_list = settings.get("user_currencies")
    stocks_list = settings.get("user_stocks")

    input_date = input('Введите дату для анализа и вывода данных в формате DD.MM.YYYY: ')


    currency_data = get_currency_data(input_date, currency_list)
    generate_json_response(currency_data)

    stock_data = get_stock_data(stocks_list)
    generate_json_response(stock_data)


if __name__ == "__main__":
    main()
