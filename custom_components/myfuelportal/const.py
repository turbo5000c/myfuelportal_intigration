"""Constants for the MyFuelPortal integration."""

from __future__ import annotations

# Domain name for this integration
DOMAIN = "myfuelportal"

# Configuration keys
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
CONF_FUEL_VENDOR = "fuel_vendor"

# Default values
DEFAULT_NAME = "MyFuelPortal"

#DEFAULT_UPDATE_INTERVAL = 300  # seconds (5 minutes)
DEFAULT_UPDATE_INTERVAL = 7200  # seconds (2 hours)

# Validation patterns
FUEL_VENDOR_PATTERN = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'

# Sensor attribute keys
ATTR_TANK_LEVEL = "tank_level_percent"
ATTR_GALLONS_REMAINING = "gallons_remaining"
ATTR_TANK_CAPACITY = "tank_capacity"
ATTR_FUEL_TYPE = "fuel_type"
ATTR_LAST_DELIVERY_DATE = "last_delivery_date"
ATTR_READING_DATE = "reading_date"
ATTR_CURRENT_PRICE = "current_price"
