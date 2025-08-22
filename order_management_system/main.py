#!/usr/bin/env python3
"""
Главный модуль системы управления заказами
Точка входа в приложение
"""

import sys
import os
from gui import OrderManagementApp
import tkinter as tk


def main():
    """Основная функция приложения"""
    try:
        # Создаем необходимые директории
        os.makedirs('data/export', exist_ok=True)
        os.makedirs('data/imports', exist_ok=True)

        # Запуск GUI приложения
        root = tk.Tk()
        app = OrderManagementApp(root)
        root.mainloop()

    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()