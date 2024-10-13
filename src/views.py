from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from src.utils import load_user_settings, get_currency_data, get_stock_data
import pandas as pd

app = Flask(__name__)


def get_date_range(input_date, range_type='M'):
    if range_type == 'W':
        start_date = input_date - timedelta(days=input_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif range_type == 'M':
        start_date = input_date.replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    elif range_type == 'Y':
        start_date = input_date.replace(month=1, day=1)
        end_date = input_date.replace(month=12, day=31)
    elif range_type == 'ALL':
        start_date = datetime(2000, 1, 1)
        end_date = input_date
    else:
        raise ValueError("Неверное значение")

    return start_date, end_date


def analyze_expenses(expenses_df):
    expenses_df = expenses_df[expenses_df['Сумма операции'] < 0]
    total_expenses = -expenses_df['Сумма операции'].sum()
    top_categories = expenses_df.groupby('Категория')['Сумма операции'].sum().nlargest(7)
    other_total = expenses_df[~expenses_df['Категория'].isin(top_categories.index)]['Сумма операции'].sum()
    top_categories = top_categories.append(pd.Series({"Остальное": other_total}))

    cash_transfer_categories = expenses_df[expenses_df['Категория'].isin(['Наличные', 'Переводы'])]
    cash_transfer_total = -cash_transfer_categories['Сумма операции'].sum()

    return total_expenses, top_categories, cash_transfer_total


def analyze_income(income_df):
    income_df = income_df[income_df['Сумма операции'] > 0]
    total_income = income_df['Сумма операции'].sum()
    top_income_categories = income_df.groupby('Категория')['Сумма операции'].sum().nlargest(7)

    return total_income, top_income_categories


@app.route('/get_events', methods=['GET'])
def get_events():
    try:
        file_name = request.args.get('filename')
        operations_data = pd.read_excel(file_name)

        input_date_str = request.args.get('Дата платежа')
        range_type = request.args.get('range', 'M')

        input_date = datetime.strptime(input_date_str, '%d.%m.%Y')
        start_date, end_date = get_date_range(input_date, range_type)

        settings = load_user_settings()
        currencies = settings['user_currencies']
        stocks = settings['user_stocks']

        filtered_data = operations_data[operations_data['Дата'].between(start_date, end_date)]

        total_expenses, top_expenses, cash_transfer_total = analyze_expenses(filtered_data)
        total_income, top_income = analyze_income(filtered_data)

        currency_data = get_currency_data(input_date_str, currencies)
        stock_data = get_stock_data(stocks)

        response_data = {
            'Расходы': {
                'Общая сумма': round(total_expenses),
                'Основные': top_expenses.to_dict(),
                'Переводы и наличные': round(cash_transfer_total)
            },
            'Поступления': {
                'Общая сумма': round(total_income),
                'Основные': top_income.to_dict()
            },
            'Курс валют': currency_data,
            'Стоимость акций': stock_data
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
