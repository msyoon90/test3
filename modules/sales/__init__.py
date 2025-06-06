# File: modules/sales/__init__.py

from .layouts import create_sales_layout
from .callbacks import register_sales_callbacks

__all__ = ['create_sales_layout', 'register_sales_callbacks']
