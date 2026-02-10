"""Config flow for MyFuelPortal integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api import MyFuelPortalAPI, AuthenticationError, ConnectionError as APIConnectionError
from .const import CONF_EMAIL, CONF_PASSWORD, CONF_FUEL_VENDOR, DOMAIN, FUEL_VENDOR_PATTERN

_LOGGER = logging.getLogger(__name__)

# Data schema for the user configuration step
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_FUEL_VENDOR): vol.All(
            str,
            vol.Match(
                FUEL_VENDOR_PATTERN,
                msg="Fuel vendor must contain only alphanumeric characters and hyphens"
            )
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    api = MyFuelPortalAPI(data[CONF_EMAIL], data[CONF_PASSWORD], data[CONF_FUEL_VENDOR])
    
    try:
        # Try to authenticate with the provided credentials
        result = await api.async_login()
        if not result:
            raise InvalidAuth
    except AuthenticationError as err:
        raise InvalidAuth from err
    except APIConnectionError as err:
        raise CannotConnect from err
    finally:
        await api.async_close()

    # Return info to be stored in the config entry
    return {"title": data[CONF_EMAIL]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyFuelPortal."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create the config entry with a unique ID based on email
                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        # Show the configuration form
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
