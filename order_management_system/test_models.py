import unittest
from datetime import datetime
from models import Customer, Product, Order, OrderItem, ModelFactory


class TestModels(unittest.TestCase):

    def setUp(self):
        """Настройка тестовых данных"""
        self.customer = Customer(
            name="Иван Иванов",
            email="ivan@example.com",
            phone="+79161234567",
            address="Москва, ул. Примерная, 123"
        )

        self.product = Product(
            name="Тестовый товар",
            description="Описание тестового товара",
            price=100.0,
            category="Тест",
            stock=10
        )

        self.order = Order(customer=self.customer)
        self.order.add_item(self.product, 2)

    def test_customer_validation(self):
        """Тест валидации клиента"""
        self.assertTrue(self.customer.validate())

        # Невалидный email
        invalid_customer = Customer(name="Test", email="invalid-email")
        self.assertFalse(invalid_customer.validate())

    def test_product_validation(self):
        """Тест валидации товара"""
        self.assertTrue(self.product.validate())

        # Отрицательная цена
        invalid_product = Product(name="Test", price=-10)
        self.assertFalse(invalid_product.validate())

    def test_order_validation(self):
        """Тест валидации заказа"""
        self.assertTrue(self.order.validate())

        # Пустой заказ
        empty_order = Order(customer=self.customer)
        self.assertFalse(empty_order.validate())

    def test_order_total_calculation(self):
        """Тест расчета общей суммы заказа"""
        self.assertEqual(self.order.total_amount, 200.0)

        # Добавляем еще один товар
        another_product = Product(name="Другой товар", price=50.0)
        self.order.add_item(another_product, 1)
        self.assertEqual(self.order.total_amount, 250.0)

    def test_model_factory(self):
        """Тест фабрики моделей"""
        customer = ModelFactory.create_model("customer", name="Фабричный клиент")
        self.assertIsInstance(customer, Customer)

        product = ModelFactory.create_model("product", name="Фабричный товар", price=100)
        self.assertIsInstance(product, Product)

        with self.assertRaises(ValueError):
            ModelFactory.create_model("unknown")

    def test_to_dict_methods(self):
        """Тест методов преобразования в словарь"""
        customer_dict = self.customer.to_dict()
        self.assertIn('name', customer_dict)
        self.assertIn('email', customer_dict)

        product_dict = self.product.to_dict()
        self.assertIn('price', product_dict)
        self.assertIn('stock', product_dict)

        order_dict = self.order.to_dict()
        self.assertIn('total_amount', order_dict)
        self.assertIn('items', order_dict)

    def test_order_item_calculation(self):
        """Тест расчета стоимости элемента заказа"""
        item = OrderItem(self.product, 3)
        self.assertEqual(item.total_price, 300.0)

        item_dict = item.to_dict()
        self.assertEqual(item_dict['quantity'], 3)
        self.assertEqual(item_dict['total_price'], 300.0)


if __name__ == '__main__':
    unittest.main()