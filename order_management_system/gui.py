import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from tkinter import font as tkfont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from datetime import datetime
from typing import List, Dict, Any, Optional

from models import Customer, Product, Order, OrderItem, ModelFactory
from db import Database
from analysis import DataAnalyzer


class OrderManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления заказами")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        self.db = Database()
        self.analyzer = DataAnalyzer()

        self.current_customer = None
        self.current_order = None
        self.cart_items = []

        self.setup_styles()
        self.create_widgets()
        self.load_data()

    def setup_styles(self):
        """Настройка стилей приложения"""
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))

        self.bold_font = tkfont.Font(family='Arial', size=10, weight='bold')
        self.normal_font = tkfont.Font(family='Arial', size=10)

    def create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главный фрейм с вкладками
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка клиентов
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text='Клиенты')
        self.setup_customers_tab()

        # Вкладка товаров
        self.products_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.products_frame, text='Товары')
        self.setup_products_tab()

        # Вкладка заказов
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text='Заказы')
        self.setup_orders_tab()

        # Вкладка анализа
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text='Аналитика')
        self.setup_analysis_tab()

        # Вкладка импорта/экспорта
        self.import_export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_export_frame, text='Импорт/Экспорт')
        self.setup_import_export_tab()

    def setup_customers_tab(self):
        """Настройка вкладки клиентов"""
        # Фрейм для формы добавления клиента
        form_frame = ttk.LabelFrame(self.customers_frame, text="Добавить клиента")
        form_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.customer_name = ttk.Entry(form_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.customer_email = ttk.Entry(form_frame, width=30)
        self.customer_email.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.customer_phone = ttk.Entry(form_frame, width=30)
        self.customer_phone.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Адрес:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.customer_address = ttk.Entry(form_frame, width=30)
        self.customer_address.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(form_frame, text="Добавить клиента",
                   command=self.add_customer).grid(row=4, column=1, padx=5, pady=10, sticky='e')

        # Таблица клиентов
        table_frame = ttk.LabelFrame(self.customers_frame, text="Список клиентов")
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'name', 'email', 'phone', 'address', 'registration_date')
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.customers_tree.heading(col, text=col.replace('_', ' ').title())
            self.customers_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)

        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        button_frame = ttk.Frame(self.customers_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить", command=self.load_customers).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV",
                   command=lambda: self.export_data('customers', 'csv')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в JSON",
                   command=lambda: self.export_data('customers', 'json')).pack(side='left', padx=5)

    def setup_products_tab(self):
        """Настройка вкладки товаров"""
        # Аналогично setup_customers_tab, но для товаров
        form_frame = ttk.LabelFrame(self.products_frame, text="Добавить товар")
        form_frame.pack(fill='x', padx=10, pady=5)

        # Поля формы для товара...
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.product_name = ttk.Entry(form_frame, width=30)
        self.product_name.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_description = ttk.Entry(form_frame, width=30)
        self.product_description.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Цена:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.product_price = ttk.Entry(form_frame, width=30)
        self.product_price.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Категория:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.product_category = ttk.Entry(form_frame, width=30)
        self.product_category.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Количество:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.product_stock = ttk.Entry(form_frame, width=30)
        self.product_stock.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(form_frame, text="Добавить товар",
                   command=self.add_product).grid(row=5, column=1, padx=5, pady=10, sticky='e')

        # Таблица товаров
        table_frame = ttk.LabelFrame(self.products_frame, text="Список товаров")
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'name', 'description', 'price', 'category', 'stock')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings')

        for col in columns:
            self.products_tree.heading(col, text=col.replace('_', ' ').title())
            self.products_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        button_frame = ttk.Frame(self.products_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить", command=self.load_products).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_product).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в CSV",
                   command=lambda: self.export_data('products', 'csv')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Экспорт в JSON",
                   command=lambda: self.export_data('products', 'json')).pack(side='left', padx=5)

    def setup_orders_tab(self):
        """Настройка вкладки заказов"""
        # Фрейм для создания заказа
        order_frame = ttk.LabelFrame(self.orders_frame, text="Создать заказ")
        order_frame.pack(fill='x', padx=10, pady=5)

        # Выбор клиента
        ttk.Label(order_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(order_frame, textvariable=self.customer_var, state='readonly')
        self.customer_combo.grid(row=0, column=1, padx=5, pady=5)
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_select)

        # Выбор товара
        ttk.Label(order_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(order_frame, textvariable=self.product_var, state='readonly')
        self.product_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(order_frame, text="Количество:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.quantity_var = tk.StringVar(value="1")
        self.quantity_spin = ttk.Spinbox(order_frame, from_=1, to=100, textvariable=self.quantity_var)
        self.quantity_spin.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(order_frame, text="Добавить в заказ",
                   command=self.add_to_cart).grid(row=3, column=1, padx=5, pady=10, sticky='e')

        # Корзина товаров
        cart_frame = ttk.LabelFrame(self.orders_frame, text="Корзина")
        cart_frame.pack(fill='x', padx=10, pady=5)

        columns = ('product', 'quantity', 'price', 'total')
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show='headings')

        for col in columns:
            self.cart_tree.heading(col, text=col.title())
            self.cart_tree.column(col, width=100)

        ttk.Button(cart_frame, text="Удалить из корзины",
                   command=self.remove_from_cart).pack(side='bottom', pady=5)

        self.cart_tree.pack(fill='x', pady=5)

        # Итоговая сумма
        total_frame = ttk.Frame(self.orders_frame)
        total_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(total_frame, text="Общая сумма:", font=self.bold_font).pack(side='left')
        self.total_label = ttk.Label(total_frame, text="0.00 руб.", font=self.bold_font)
        self.total_label.pack(side='left', padx=5)

        ttk.Button(total_frame, text="Создать заказ",
                   command=self.create_order).pack(side='right')

        # Таблица заказов
        orders_table_frame = ttk.LabelFrame(self.orders_frame, text="История заказов")
        orders_table_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('id', 'customer', 'date', 'status', 'amount')
        self.orders_tree = ttk.Treeview(orders_table_frame, columns=columns, show='headings')

        for col in columns:
            self.orders_tree.heading(col, text=col.title())
            self.orders_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(orders_table_frame, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        button_frame = ttk.Frame(self.orders_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить", command=self.load_orders).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Просмотреть детали",
                   command=self.view_order_details).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Изменить статус",
                   command=self.change_order_status).pack(side='left', padx=5)

    def setup_analysis_tab(self):
        """Настройка вкладки анализа"""
        analysis_frame = ttk.Frame(self.analysis_frame)
        analysis_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Кнопки для различных анализов
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Топ клиенты",
                   command=self.show_top_customers).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Динамика продаж",
                   command=self.show_sales_trend).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Топ товары",
                   command=self.show_top_products).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Граф клиентов",
                   command=self.show_customer_network).pack(side='left', padx=5)
        ttk.Button(button_frame, text="География",
                   command=self.show_customer_geography).pack(side='left', padx=5)

        # Область для отображения графиков
        self.chart_frame = ttk.Frame(analysis_frame)
        self.chart_frame.pack(fill='both', expand=True)

    def setup_import_export_tab(self):
        """Настройка вкладки импорта/экспорта"""
        main_frame = ttk.Frame(self.import_export_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Экспорт
        export_frame = ttk.LabelFrame(main_frame, text="Экспорт данных")
        export_frame.pack(fill='x', pady=5)

        ttk.Label(export_frame, text="Таблица:").grid(row=0, column=0, padx=5, pady=5)
        self.export_table = ttk.Combobox(export_frame, values=['customers', 'products', 'orders'], state='readonly')
        self.export_table.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(export_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5)
        self.export_format = ttk.Combobox(export_frame, values=['CSV', 'JSON'], state='readonly')
        self.export_format.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(export_frame, text="Экспорт",
                   command=self.export_data).grid(row=0, column=4, padx=5, pady=5)

        # Импорт
        import_frame = ttk.LabelFrame(main_frame, text="Импорт данных")
        import_frame.pack(fill='x', pady=5)

        ttk.Label(import_frame, text="Таблица:").grid(row=0, column=0, padx=5, pady=5)
        self.import_table = ttk.Combobox(import_frame, values=['customers', 'products', 'orders'], state='readonly')
        self.import_table.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(import_frame, text="Формат:").grid(row=0, column=2, padx=5, pady=5)
        self.import_format = ttk.Combobox(import_frame, values=['CSV', 'JSON'], state='readonly')
        self.import_format.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(import_frame, text="Выбрать файл",
                   command=self.select_import_file).grid(row=0, column=4, padx=5, pady=5)
        ttk.Button(import_frame, text="Импорт",
                   command=self.import_data).grid(row=0, column=5, padx=5, pady=5)

        self.import_file = ttk.Label(import_frame, text="Файл не выбран")
        self.import_file.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

        # Журнал операций
        log_frame = ttk.LabelFrame(main_frame, text="Журнал операций")
        log_frame.pack(fill='both', expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.log_text.config(state='disabled')

    def load_data(self):
        """Загрузка данных при запуске"""
        self.load_customers()
        self.load_products()
        self.load_orders()

    def load_customers(self):
        """Загрузка списка клиентов"""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        customers = self.db.get_all_customers()
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer.id, customer.name, customer.email,
                customer.phone, customer.address, customer.registration_date
            ))

        # Обновление комбобокса для заказов
        customer_names = [f"{c.id}: {c.name}" for c in customers]
        self.customer_combo['values'] = customer_names

    def load_products(self):
        """Загрузка списка товаров"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        products = self.db.get_all_products()
        for product in products:
            self.products_tree.insert('', 'end', values=(
                product.id, product.name, product.description,
                product.price, product.category, product.stock
            ))

        # Обновление комбобокса для заказов
        product_names = [f"{p.id}: {p.name} (${p.price})" for p in products]
        self.product_combo['values'] = product_names

    def load_orders(self):
        """Загрузка списка заказов"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        orders = self.db.get_all_orders()
        for order in orders:
            self.orders_tree.insert('', 'end', values=(
                order.id,
                order.customer.name if order.customer else "Unknown",
                order.order_date,
                order.status,
                f"${order.total_amount:.2f}"
            ))

    def add_customer(self):
        """Добавление нового клиента"""
        try:
            customer = Customer(
                name=self.customer_name.get(),
                email=self.customer_email.get(),
                phone=self.customer_phone.get(),
                address=self.customer_address.get()
            )

            if customer.validate():
                customer_id = self.db.add_customer(customer)
                self.log_operation(f"Добавлен клиент: {customer.name} (ID: {customer_id})")
                self.load_customers()
                self.clear_customer_form()
                messagebox.showinfo("Успех", "Клиент успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Неверные данные клиента")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении клиента: {str(e)}")

    def add_product(self):
        """Добавление нового товара"""
        try:
            product = Product(
                name=self.product_name.get(),
                description=self.product_description.get(),
                price=float(self.product_price.get()),
                category=self.product_category.get(),
                stock=int(self.product_stock.get())
            )

            if product.validate():
                product_id = self.db.add_product(product)
                self.log_operation(f"Добавлен товар: {product.name} (ID: {product_id})")
                self.load_products()
                self.clear_product_form()
                messagebox.showinfo("Успех", "Товар успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Неверные данные товара")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат цены или количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении товара: {str(e)}")

    def on_customer_select(self, event):
        """Обработка выбора клиента"""
        selection = self.customer_var.get()
        if selection:
            customer_id = int(selection.split(':')[0])
            self.current_customer = self.db.get_customer(customer_id)

    def add_to_cart(self):
        """Добавление товара в корзину"""
        try:
            if not self.current_customer:
                messagebox.showerror("Ошибка", "Сначала выберите клиента")
                return

            selection = self.product_var.get()
            if not selection:
                messagebox.showerror("Ошибка", "Выберите товар")
                return

            product_id = int(selection.split(':')[0])
            product = self.db.get_product(product_id)
            quantity = int(self.quantity_var.get())

            if quantity <= 0:
                messagebox.showerror("Ошибка", "Количество должно быть положительным")
                return

            # Добавляем в корзину
            self.cart_items.append((product, quantity))

            # Обновляем отображение корзины
            self.update_cart_display()

        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат количества")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении в корзину: {str(e)}")

    def update_cart_display(self):
        """Обновление отображения корзины"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        total = 0
        for product, quantity in self.cart_items:
            item_total = product.price * quantity
            total += item_total
            self.cart_tree.insert('', 'end', values=(
                product.name, quantity, f"${product.price:.2f}", f"${item_total:.2f}"
            ))

        self.total_label.config(text=f"${total:.2f}")

    def remove_from_cart(self):
        """Удаление товара из корзины"""
        selection = self.cart_tree.selection()
        if selection:
            index = self.cart_tree.index(selection[0])
            self.cart_items.pop(index)
            self.update_cart_display()

    def create_order(self):
        """Создание заказа"""
        try:
            if not self.current_customer:
                messagebox.showerror("Ошибка", "Сначала выберите клиента")
                return

            if not self.cart_items:
                messagebox.showerror("Ошибка", "Корзина пуста")
                return

            order = Order(customer=self.current_customer)
            for product, quantity in self.cart_items:
                order.add_item(product, quantity)

            if order.validate():
                order_id = self.db.add_order(order)
                self.log_operation(f"Создан заказ: #{order_id} для {self.current_customer.name}")

                # Очищаем корзину
                self.cart_items = []
                self.update_cart_display()
                self.load_orders()

                messagebox.showinfo("Успех", f"Заказ #{order_id} успешно создан")
            else:
                messagebox.showerror("Ошибка", "Неверные данные заказа")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании заказа: {str(e)}")

    def export_data(self, table=None, format=None):
        """Экспорт данных"""
        try:
            if table is None:
                table = self.export_table.get()
                format = self.export_format.get().lower()

            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format}",
                filetypes=[(f"{format.upper()} files", f"*.{format}")]
            )

            if filename:
                if format == 'csv':
                    self.db.export_to_csv(table, filename)
                elif format == 'json':
                    self.db.export_to_json(table, filename)

                self.log_operation(f"Экспортирована таблица {table} в {format.upper()}")
                messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

    def select_import_file(self):
        """Выбор файла для импорта"""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
        )
        if filename:
            self.import_file.config(text=filename)

    def import_data(self):
        """Импорт данных"""
        try:
            filename = self.import_file.cget("text")
            if filename == "Файл не выбран":
                messagebox.showerror("Ошибка", "Сначала выберите файл")
                return

            table = self.import_table.get()
            format = self.import_format.get().lower()

            if filename.endswith('.csv'):
                self.db.import_from_csv(table, filename)
            elif filename.endswith('.json'):
                self.db.import_from_json(table, filename)

            self.log_operation(f"Импортирована таблица {table} из {filename}")
            messagebox.showinfo("Успех", "Данные успешно импортированы")

            # Обновляем данные
            if table == 'customers':
                self.load_customers()
            elif table == 'products':
                self.load_products()
            elif table == 'orders':
                self.load_orders()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при импорте: {str(e)}")

    def show_top_customers(self):
        """Показать топ клиентов"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            top_customers = self.analyzer.get_top_customers()

            ax.barh(top_customers['name'], top_customers['order_count'])
            ax.set_title('Топ клиентов по количеству заказов')
            ax.set_xlabel('Количество заказов')
            ax.set_ylabel('Клиенты')

            self.display_chart(fig)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {str(e)}")

    def show_sales_trend(self):
        """Показать динамику продаж"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            sales_data = self.analyzer.get_sales_trend('W')

            sales_data.plot(kind='line', marker='o', ax=ax)
            ax.set_title('Динамика продаж (по неделям)')
            ax.set_xlabel('Дата')
            ax.set_ylabel('Сумма продаж')
            ax.grid(True)
            plt.xticks(rotation=45)

            self.display_chart(fig)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {str(e)}")

    def display_chart(self, fig):
        """Отображение графика в интерфейсе"""
        # Очищаем предыдущий график
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Создаем canvas для matplotlib
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def log_operation(self, message):
        """Логирование операций"""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see('end')

    def clear_customer_form(self):
        """Очистка формы клиента"""
        self.customer_name.delete(0, 'end')
        self.customer_email.delete(0, 'end')
        self.customer_phone.delete(0, 'end')
        self.customer_address.delete(0, 'end')

    def clear_product_form(self):
        """Очистка формы товара"""
        self.product_name.delete(0, 'end')
        self.product_description.delete(0, 'end')
        self.product_price.delete(0, 'end')
        self.product_category.delete(0, 'end')
        self.product_stock.delete(0, 'end')

    def delete_customer(self):
        """Удаление клиента"""
        selection = self.customers_tree.selection()
        if selection:
            customer_id = self.customers_tree.item(selection[0])['values'][0]
            if messagebox.askyesno("Подтверждение", "Удалить выбранного клиента?"):
                # Реализация удаления из базы данных
                messagebox.showinfo("Инфо", "Функция удаления будет реализована")
        else:
            messagebox.showerror("Ошибка", "Выберите клиента для удаления")

    def delete_product(self):
        """Удаление товара"""
        selection = self.products_tree.selection()
        if selection:
            product_id = self.products_tree.item(selection[0])['values'][0]
            if messagebox.askyesno("Подтверждение", "Удалить выбранный товар?"):
                # Реализация удаления из базы данных
                messagebox.showinfo("Инфо", "Функция удаления будет реализована")
        else:
            messagebox.showerror("Ошибка", "Выберите товар для удаления")

    def view_order_details(self):
        """Просмотр деталей заказа"""
        selection = self.orders_tree.selection()
        if selection:
            order_id = self.orders_tree.item(selection[0])['values'][0]
            order = self.db.get_order(order_id)

            details = f"Заказ #{order.id}\n"
            details += f"Клиент: {order.customer.name}\n"
            details += f"Дата: {order.order_date}\n"
            details += f"Статус: {order.status}\n"
            details += f"Общая сумма: ${order.total_amount:.2f}\n\n"
            details += "Товары:\n"

            for item in order.items:
                details += f"- {item.product.name} x{item.quantity} (${item.total_price:.2f})\n"

            messagebox.showinfo("Детали заказа", details)
        else:
            messagebox.showerror("Ошибка", "Выберите заказ для просмотра")

    def change_order_status(self):
        """Изменение статуса заказа"""
        selection = self.orders_tree.selection()
        if selection:
            order_id = self.orders_tree.item(selection[0])['values'][0]
            # Реализация изменения статуса
            messagebox.showinfo("Инфо", "Функция изменения статуса будет реализована")
        else:
            messagebox.showerror("Ошибка", "Выберите заказ для изменения статуса")

    def show_top_products(self):
        """Показать топ товаров"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            top_products = self.analyzer.get_top_products()

            ax.bar(top_products['name'], top_products['total_revenue'])
            ax.set_title('Топ товаров по выручке')
            ax.set_xlabel('Товары')
            ax.set_ylabel('Выручка')
            plt.xticks(rotation=45, ha='right')

            self.display_chart(fig)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {str(e)}")

    def show_customer_network(self):
        """Показать граф клиентов"""
        try:
            fig, ax = plt.subplots(figsize=(14, 10))
            G = self.analyzer.create_customer_network()
            pos = nx.spring_layout(G, k=1, iterations=50)

            nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.9, ax=ax)

            edges = G.edges(data=True)
            weights = [data['weight'] for _, _, data in edges]
            nx.draw_networkx_edges(G, pos, width=[w / 2 for w in weights], alpha=0.6, ax=ax)

            labels = {node: G.nodes[node]['name'] for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8, ax=ax)

            ax.set_title('Граф связей клиентов (по общим товарам)')
            ax.axis('off')

            self.display_chart(fig)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {str(e)}")

    def show_customer_geography(self):
        """Показать географическое распределение"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8))
            geo_data = self.analyzer.get_customer_geography()

            ax.pie(geo_data['count'], labels=geo_data['city'], autopct='%1.1f%%')
            ax.set_title('Географическое распределение клиентов')

            self.display_chart(fig)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении графика: {str(e)}")


def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = OrderManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()