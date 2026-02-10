"""The MyFuelPortal integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import MyFuelPortalAPI
from .const import CONF_EMAIL, CONF_PASSWORD, CONF_FUEL_VENDOR, DOMAIN
from .coordinator import MyCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

# List of platforms to support
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the MyFuelPortal component."""
    # Initialize the integration's data storage
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyFuelPortal from a config entry."""
    _LOGGER.debug("Setting up %s integration", DOMAIN)

    # Initialize the API client
    api = MyFuelPortalAPI(
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_FUEL_VENDOR],
    )

    # Authenticate with the API
    try:
        await api.async_login()
    except Exception as err:
        await api.async_close()
        raise ConfigEntryNotReady(f"Failed to authenticate: {err}") from err

    # Create the data update coordinator
    coordinator = MyCoordinator(hass, entry, api)

    # Fetch initial data to verify the connection works
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass.data for access by platforms
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms for this integration
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading %s integration", DOMAIN)

    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # Close the API session and remove the config entry from hass.data
    if unload_ok:
        coordinator: MyCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.api.async_close()

    return unload_ok
