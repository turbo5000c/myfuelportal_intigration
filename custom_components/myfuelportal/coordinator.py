"""Data update coordinator for MyFuelPortal."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MyFuelPortalAPI, AuthenticationError, ConnectionError as APIConnectionError
from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, api: MyFuelPortalAPI
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.entry = entry
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Fetch tank data from the API
            data = await self.api.async_get_tank_data()
            return data

        except AuthenticationError as err:
            # Try to re-authenticate once if session expired
            _LOGGER.warning("Session expired, attempting to re-authenticate")
            try:
                await self.api.async_login()
                data = await self.api.async_get_tank_data()
                return data
            except Exception as reauth_err:
                raise UpdateFailed(
                    f"Authentication failed: {reauth_err}"
                ) from reauth_err

        except APIConnectionError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
