"""Sensor platform for MyFuelPortal."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_GALLONS_REMAINING, ATTR_TANK_LEVEL, ATTR_TANK_CAPACITY, ATTR_FUEL_TYPE, ATTR_LAST_DELIVERY_DATE, ATTR_READING_DATE, ATTR_CURRENT_PRICE, DOMAIN
from .coordinator import MyCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: MyCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    sensors = [
        TankLevelSensor(coordinator, entry),
        GallonsRemainingSensor(coordinator, entry),
        TankCapacitySensor(coordinator, entry),
        FuelTypeSensor(coordinator, entry),
        LastDeliveryDateSensor(coordinator, entry),
        ReadingDateSensor(coordinator, entry),
        CurrentPriceSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class TankLevelSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of tank level percentage sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_tank_level"
        
        # Set the entity name
        self._attr_name = "Tank Level"
        
        # Set sensor properties
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:propane-tank"
        
        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_TANK_LEVEL)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class GallonsRemainingSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of gallons remaining sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_gallons_remaining"
        
        # Set the entity name
        self._attr_name = "Gallons Remaining"
        
        # Set sensor properties
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfVolume.GALLONS
        self._attr_icon = "mdi:gauge"
        
        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_GALLONS_REMAINING)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class TankCapacitySensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of tank capacity sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        
        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_tank_capacity"
        
        # Set the entity name
        self._attr_name = "Tank Capacity"
        
        # Set sensor properties (no state class as tank capacity is static)
        self._attr_native_unit_of_measurement = UnitOfVolume.GALLONS
        self._attr_icon = "mdi:propane-tank"
        
        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_TANK_CAPACITY)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class FuelTypeSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of fuel type sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_fuel_type"

        # Set the entity name
        self._attr_name = "Fuel Type"

        # Set sensor properties (no state class or unit for string values)
        self._attr_icon = "mdi:fuel"

        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_FUEL_TYPE)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class LastDeliveryDateSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of last delivery date sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_last_delivery_date"

        # Set the entity name
        self._attr_name = "Last Delivery Date"

        # Set sensor properties (no state class or unit for date strings)
        self._attr_icon = "mdi:calendar-clock"

        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_LAST_DELIVERY_DATE)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class ReadingDateSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of tank reading date sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_reading_date"

        # Set the entity name
        self._attr_name = "Reading Date"

        # Set sensor properties (no state class or unit for date strings)
        self._attr_icon = "mdi:calendar-check"

        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_READING_DATE)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success


class CurrentPriceSensor(CoordinatorEntity[MyCoordinator], SensorEntity):
    """Representation of current fuel price sensor."""

    def __init__(self, coordinator: MyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        # Set the unique ID for the entity
        self._attr_unique_id = f"{entry.entry_id}_current_price"

        # Set the entity name
        self._attr_name = "Current Price"

        # Set sensor properties
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "$/gal"
        self._attr_icon = "mdi:currency-usd"

        # Set the device info to group entities under a device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "MyFuelPortal",
            "model": "Propane Tank Monitor",
        }

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        return self.coordinator.data.get(ATTR_CURRENT_PRICE)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
