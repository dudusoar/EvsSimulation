# code/models/__init__.py
"""
Data models module

Defines the data structure for vehicles, orders and charging stations
"""

from .vehicle import Vehicle
from .order import Order
from .charging_station import ChargingStation

__all__ = ['Vehicle', 'Order', 'ChargingStation']