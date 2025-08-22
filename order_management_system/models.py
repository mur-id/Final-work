import re
from datetime import datetime
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseModel(ABC):
    """Абстрактный базовый класс для всех моделей"""

    def __init__(self, id: int = None):
        self.id = id

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass


class Person(BaseModel):
    """Базовый класс для персон с контактными данными"""

    def __init__(self, id: int = None, name: str = "", email: str = "",
                 phone: str = "", address: str = ""):
        super().__init__(id)
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address

    def validate(self) -> bool:
        """Проверка валидности данных с использованием регулярных выражений"""
        if not self.name.strip():
            return False

        # Проверка email с регулярным выражением
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if self.email and not re.match(email_pattern, self.email):
            return False

        # Проверка телефона с регулярным выражением
        phone_pattern = r'^\+?[1-9]\d{1,14}$'
        if self.phone and not re.match(phone_pattern, self.phone.replace(" ", "")):
            return False

        return True


class Customer(Person):
    """Класс клиента"""

    def __init__(self, id: int = None, name: str = "", email: str = "",
                 phone: str = "", address: str = "", registration_date: str = None):
        super().__init__(id, name, email, phone, address)
        self.registration_date = registration_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'registration_date': self.registration_date
        }

    def __str__(self):
        return f"Customer({self.id}: {self.name}, {self.email})"


class Product(BaseModel):
    """Класс товара"""

    def __init__(self, id: int = None, name: str = "", description: str = "",
                 price: float = 0.0, category: str = "", stock: int = 0):
        super().__init__(id)
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.stock = stock

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock': self.stock
        }

    def validate(self) -> bool:
        if not self.name.strip() or self.price < 0 or self.stock < 0:
            return False
        return True

    def __str__(self):
        return f"Product({self.id}: {self.name}, ${self.price})"


class OrderItem:
    """Класс элемента заказа"""

    def __init__(self, product: Product, quantity: int = 1):
        self.product = product
        self.quantity = quantity
        self.total_price = product.price * quantity

    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'unit_price': self.product.price,
            'total_price': self.total_price
        }


class Order(BaseModel):
    """Класс заказа"""

    def __init__(self, id: int = None, customer: Customer = None,
                 order_date: str = None, status: str = "pending"):
        super().__init__(id)
        self.customer = customer
        self.order_date = order_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status
        self.items: List[OrderItem] = []
        self.total_amount = 0.0

    def add_item(self, product: Product, quantity: int = 1):
        """Добавление товара в заказ"""
        item = OrderItem(product, quantity)
        self.items.append(item)
        self.total_amount += item.total_price

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'customer_id': self.customer.id if self.customer else None,
            'customer_name': self.customer.name if self.customer else "",
            'order_date': self.order_date,
            'status': self.status,
            'total_amount': self.total_amount,
            'items': [item.to_dict() for item in self.items]
        }

    def validate(self) -> bool:
        if not self.customer or not self.items:
            return False
        return True

    def __str__(self):
        return f"Order({self.id}: {self.customer.name if self.customer else 'Unknown'}, ${self.total_amount})"


# Фабричный метод для создания моделей
class ModelFactory:
    @staticmethod
    def create_model(model_type: str, **kwargs) -> BaseModel:
        if model_type == "customer":
            return Customer(**kwargs)
        elif model_type == "product":
            return Product(**kwargs)
        elif model_type == "order":
            return Order(**kwargs)
        raise ValueError(f"Unknown model type: {model_type}")