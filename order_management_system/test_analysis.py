import unittest
import pandas as pd
import sqlite3
import os
from analysis import DataAnalyzer, sort_orders_by_date, sort_orders_by_amount, analyze_nested_data


class TestAnalysis(unittest.TestCase):

    def setUp(self):
        """Настройка тестовой базы данных"""
        self.test_db = "test_database.db"

        # Создаем тестовую базу
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Создаем таблицы
        cursor.execute('''
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                registration_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                price REAL,
                category TEXT,
                stock INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date TEXT,
                status TEXT,
                total_amount REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL
            )
        ''')

        # Добавляем тестовые данные
        cursor.executemany('''
            INSERT INTO customers (id, name, email, address) VALUES (?, ?, ?, ?)
        ''', [
            (1, 'Иван Иванов', 'ivan@test.com', 'Москва'),
            (2, 'Петр Петров', 'petr@test.com', 'СПб'),
            (3, 'Мария Сидорова', 'maria@test.com', 'Москва')
        ])

        cursor.executemany('''
            INSERT INTO products (id, name, price, category) VALUES (?, ?, ?, ?)
        ''', [
            (1, 'Товар 1', 100.0, 'Категория 1'),
            (2, 'Товар 2', 200.0, 'Категория 2'),
            (3, 'Товар 3', 300.0, 'Категория 1')
        ])

        cursor.executemany('''
            INSERT INTO orders (id, customer_id, order_date, status, total_amount) VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 1, '2024-01-01', 'completed', 500.0),
            (2, 1, '2024-01-02', 'pending', 300.0),
            (3, 2, '2024-01-03', 'completed', 600.0)
        ])

        cursor.executemany('''
            INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)
        ''', [
            (1, 1, 2, 100.0),
            (1, 2, 1, 200.0),
            (2, 3, 1, 300.0),
            (3, 1, 3, 100.0),
            (3, 2, 2, 200.0)
        ])

        conn.commit()
        conn.close()

        self.analyzer = DataAnalyzer(self.test_db)

    def tearDown(self):
        """Очистка тестовой базы данных"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_get_orders_dataframe(self):
        """Тест получения DataFrame заказов"""
        df = self.analyzer.get_orders_dataframe()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertIn('customer_name', df.columns)

    def test_get_top_customers(self):
        """Тест получения топ клиентов"""
        top_customers = self.analyzer.get_top_customers()
        self.assertIsInstance(top_customers, pd.DataFrame)
        self.assertTrue(len(top_customers) > 0)
        self.assertIn('order_count', top_customers.columns)

    def test_get_sales_trend(self):
        """Тест получения тренда продаж"""
        sales_trend = self.analyzer.get_sales_trend('D')
        self.assertIsInstance(sales_trend, pd.Series)

    def test_get_top_products(self):
        """Тест получения топ товаров"""
        top_products = self.analyzer.get_top_products()
        self.assertIsInstance(top_products, pd.DataFrame)
        self.assertTrue(len(top_products) > 0)

    def test_sort_orders_functions(self):
        """Тест функций сортировки"""
        # Создаем тестовые заказы
        orders = [
            type('Order', (), {'order_date': '2024-01-01', 'total_amount': 100})(),
            type('Order', (), {'order_date': '2024-01-03', 'total_amount': 300})(),
            type('Order', (), {'order_date': '2024-01-02', 'total_amount': 200})()
        ]

        # Сортировка по дате
        sorted_by_date = sort_orders_by_date(orders)
        self.assertEqual(sorted_by_date[0].order_date, '2024-01-03')

        # Сортировка по сумме
        sorted_by_amount = sort_orders_by_amount(orders)
        self.assertEqual(sorted_by_amount[0].total_amount, 300)

    def test_analyze_nested_data(self):
        """Тест рекурсивного анализа данных"""
        test_data = {
            'level1': {
                'items': [1, 2, 3],
                'nested': {
                    'deep': [4, 5]
                }
            }
        }

        result = analyze_nested_data(test_data)
        self.assertEqual(result['total_items'], 8)  # 1 + 3 + 1 + 2 + 1
        self.assertEqual(result['max_depth'], 3)

    def test_customer_geography(self):
        """Тест географического анализа"""
        geo_data = self.analyzer.get_customer_geography()
        self.assertIsInstance(geo_data, pd.DataFrame)
        self.assertTrue(len(geo_data) > 0)


if __name__ == '__main__':
    unittest.main()