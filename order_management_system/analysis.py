import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import Order, Customer
import sqlite3
from functools import lru_cache


class DataAnalyzer:
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path

    def get_orders_dataframe(self) -> pd.DataFrame:
        """Получение данных заказов в виде DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT o.id, o.order_date, o.status, o.total_amount,
                       c.name as customer_name, c.email, c.address
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
            '''
            return pd.read_sql_query(query, conn)

    def get_customers_dataframe(self) -> pd.DataFrame:
        """Получение данных клиентов в виде DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query('SELECT * FROM customers', conn)

    def get_top_customers(self, limit: int = 5) -> pd.DataFrame:
        """Топ N клиентов по количеству заказов"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT c.name, c.email, COUNT(o.id) as order_count, 
                       SUM(o.total_amount) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.id = o.customer_id
                GROUP BY c.id
                ORDER BY order_count DESC, total_spent DESC
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))

    def get_sales_trend(self, period: str = 'D') -> pd.DataFrame:
        """Динамика продаж по периодам"""
        df = self.get_orders_dataframe()
        df['order_date'] = pd.to_datetime(df['order_date'])
        df.set_index('order_date', inplace=True)

        if period == 'D':
            return df.resample('D')['total_amount'].sum().fillna(0)
        elif period == 'W':
            return df.resample('W')['total_amount'].sum().fillna(0)
        elif period == 'M':
            return df.resample('M')['total_amount'].sum().fillna(0)
        else:
            return df.resample('D')['total_amount'].sum().fillna(0)

    def get_top_products(self, limit: int = 10) -> pd.DataFrame:
        """Топ товаров по продажам"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT p.name, p.category, 
                       SUM(oi.quantity) as total_quantity,
                       SUM(oi.quantity * oi.unit_price) as total_revenue
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                GROUP BY p.id
                ORDER BY total_revenue DESC
                LIMIT ?
            '''
            return pd.read_sql_query(query, conn, params=(limit,))

    def plot_sales_trend(self, period: str = 'D'):
        """Визуализация динамики продаж"""
        sales_data = self.get_sales_trend(period)

        plt.figure(figsize=(12, 6))
        sales_data.plot(kind='line', marker='o')
        plt.title('Динамика продаж')
        plt.xlabel('Дата')
        plt.ylabel('Сумма продаж')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def plot_top_customers(self):
        """Визуализация топ клиентов"""
        top_customers = self.get_top_customers()

        plt.figure(figsize=(10, 6))
        plt.barh(top_customers['name'], top_customers['order_count'])
        plt.title('Топ клиентов по количеству заказов')
        plt.xlabel('Количество заказов')
        plt.ylabel('Клиенты')
        plt.tight_layout()
        plt.show()

    def plot_top_products(self):
        """Визуализация топ товаров"""
        top_products = self.get_top_products()

        plt.figure(figsize=(12, 6))
        plt.bar(top_products['name'], top_products['total_revenue'])
        plt.title('Топ товаров по выручке')
        plt.xlabel('Товары')
        plt.ylabel('Выручка')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def create_customer_network(self):
        """Создание графа связей клиентов"""
        G = nx.Graph()

        # Получаем данные о заказах и товарах
        with sqlite3.connect(self.db_path) as conn:
            # Добавляем клиентов как узлы
            customers_df = pd.read_sql_query('SELECT id, name, address FROM customers', conn)
            for _, row in customers_df.iterrows():
                G.add_node(row['id'], name=row['name'], address=row['address'])

            # Добавляем связи между клиентами, которые покупали одинаковые товары
            query = '''
                SELECT o1.customer_id as cust1, o2.customer_id as cust2, 
                       COUNT(DISTINCT oi1.product_id) as common_products
                FROM order_items oi1
                JOIN order_items oi2 ON oi1.product_id = oi2.product_id 
                    AND oi1.order_id != oi2.order_id
                JOIN orders o1 ON oi1.order_id = o1.id
                JOIN orders o2 ON oi2.order_id = o2.id
                WHERE o1.customer_id != o2.customer_id
                GROUP BY o1.customer_id, o2.customer_id
                HAVING common_products > 0
            '''
            edges_df = pd.read_sql_query(query, conn)

            for _, row in edges_df.iterrows():
                G.add_edge(row['cust1'], row['cust2'], weight=row['common_products'])

        return G

    def plot_customer_network(self):
        """Визуализация графа клиентов"""
        G = self.create_customer_network()

        plt.figure(figsize=(14, 10))
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Рисуем узлы
        nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.9)

        # Рисуем ребра с толщиной, пропорциональной весу
        edges = G.edges(data=True)
        weights = [data['weight'] for _, _, data in edges]
        nx.draw_networkx_edges(G, pos, width=[w / 2 for w in weights], alpha=0.6)

        # Подписи узлов
        labels = {node: G.nodes[node]['name'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.title('Граф связей клиентов (по общим товарам)')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

    def get_customer_geography(self) -> pd.DataFrame:
        """Географическое распределение клиентов"""
        df = self.get_customers_dataframe()

        # Простой анализ по городам (предполагаем, что город в начале адреса)
        df['city'] = df['address'].apply(lambda x: x.split(',')[0].strip() if x and ',' in x else 'Не указан')

        return df['city'].value_counts().reset_index()

    def plot_customer_geography(self):
        """Визуализация географического распределения"""
        geo_data = self.get_customer_geography()

        plt.figure(figsize=(12, 8))
        plt.pie(geo_data['count'], labels=geo_data['city'], autopct='%1.1f%%')
        plt.title('Географическое распределение клиентов')
        plt.tight_layout()
        plt.show()


# Функции для сортировки с использованием лямбда-выражений
sort_orders_by_date = lambda orders: sorted(orders, key=lambda x: x.order_date, reverse=True)
sort_orders_by_amount = lambda orders: sorted(orders, key=lambda x: x.total_amount, reverse=True)


# Рекурсивная функция для анализа вложенных данных
def analyze_nested_data(data, depth=0, results=None):
    """Рекурсивный анализ вложенных структур данных"""
    if results is None:
        results = {'total_items': 0, 'max_depth': 0}

    results['total_items'] += 1
    results['max_depth'] = max(results['max_depth'], depth)

    if isinstance(data, (list, tuple)):
        for item in data:
            analyze_nested_data(item, depth + 1, results)
    elif isinstance(data, dict):
        for key, value in data.items():
            analyze_nested_data(value, depth + 1, results)

    return results