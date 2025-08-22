import sqlite3
import json
import csv
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import Customer, Product, Order, OrderItem


class Database:
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Таблица клиентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    registration_date TEXT
                )
            ''')

            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT,
                    stock INTEGER DEFAULT 0
                )
            ''')

            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    order_date TEXT,
                    status TEXT,
                    total_amount REAL,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')

            # Таблица элементов заказа
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    unit_price REAL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            conn.commit()

    def add_customer(self, customer: Customer) -> int:
        """Добавление клиента в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (name, email, phone, address, registration_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer.name, customer.email, customer.phone,
                  customer.address, customer.registration_date))
            conn.commit()
            return cursor.lastrowid

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Получение клиента по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            if row:
                return Customer(id=row[0], name=row[1], email=row[2],
                                phone=row[3], address=row[4], registration_date=row[5])
            return None

    def get_all_customers(self) -> List[Customer]:
        """Получение всех клиентов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers ORDER BY name')
            return [Customer(id=row[0], name=row[1], email=row[2],
                             phone=row[3], address=row[4], registration_date=row[5])
                    for row in cursor.fetchall()]

    def add_product(self, product: Product) -> int:
        """Добавление товара в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price, category, stock)
                VALUES (?, ?, ?, ?, ?)
            ''', (product.name, product.description, product.price,
                  product.category, product.stock))
            conn.commit()
            return cursor.lastrowid

    def get_product(self, product_id: int) -> Optional[Product]:
        """Получение товара по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(id=row[0], name=row[1], description=row[2],
                               price=row[3], category=row[4], stock=row[5])
            return None

    def get_all_products(self) -> List[Product]:
        """Получение всех товаров"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY name')
            return [Product(id=row[0], name=row[1], description=row[2],
                            price=row[3], category=row[4], stock=row[5])
                    for row in cursor.fetchall()]

    def add_order(self, order: Order) -> int:
        """Добавление заказа в базу"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (customer_id, order_date, status, total_amount)
                VALUES (?, ?, ?, ?)
            ''', (order.customer.id, order.order_date, order.status, order.total_amount))
            order_id = cursor.lastrowid

            # Добавление элементов заказа
            for item in order.items:
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item.product.id, item.quantity, item.product.price))

            conn.commit()
            return order_id

    def get_order(self, order_id: int) -> Optional[Order]:
        """Получение заказа по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Получение основной информации о заказе
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            order_row = cursor.fetchone()
            if not order_row:
                return None

            customer = self.get_customer(order_row[1])
            order = Order(id=order_row[0], customer=customer,
                          order_date=order_row[2], status=order_row[3])
            order.total_amount = order_row[4]

            # Получение элементов заказа
            cursor.execute('''
                SELECT oi.product_id, oi.quantity, oi.unit_price, 
                       p.name, p.description
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = ?
            ''', (order_id,))

            for row in cursor.fetchall():
                product = Product(id=row[0], name=row[3], description=row[4], price=row[2])
                order.add_item(product, row[1])

            return order

    def get_all_orders(self) -> List[Order]:
        """Получение всех заказов"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM orders ORDER BY order_date DESC')
            order_ids = [row[0] for row in cursor.fetchall()]
            return [self.get_order(order_id) for order_id in order_ids]

    def export_to_csv(self, table_name: str, filename: str):
        """Экспорт данных в CSV"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(rows)

    def import_from_csv(self, table_name: str, filename: str):
        """Импорт данных из CSV"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                columns = next(reader)
                placeholders = ', '.join(['?' for _ in columns])

                for row in reader:
                    cursor.execute(f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})', row)

            conn.commit()

    def export_to_json(self, table_name: str, filename: str):
        """Экспорт данных в JSON"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {table_name}')
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            data = [dict(zip(columns, row)) for row in rows]

            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)

    def import_from_json(self, table_name: str, filename: str):
        """Импорт данных из JSON"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            with open(filename, 'r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)

                if data:
                    columns = list(data[0].keys())
                    placeholders = ', '.join(['?' for _ in columns])

                    for item in data:
                        values = [item[col] for col in columns]
                        cursor.execute(f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})',
                                       values)

            conn.commit()