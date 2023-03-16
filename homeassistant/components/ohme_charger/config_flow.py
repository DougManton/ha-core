"""Config flow for Ohme Smart EV Charger integration."""
from __future__ import annotations

import logging
import traceback

import voluptuous as vol

from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.components.sensor import SCAN_INTERVAL

from .OhmeAuth import OhmeAuth
from .OhmeCharger import OhmeCharger
from .const import CONF_APIKEY, CONF_PASSWORD, CONF_USERNAME, CONF_SCAN_INTERVAL, DOMAIN
from .exceptions import TimeoutException

_LOGGER: logging.Logger = logging.getLogger(__package__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


class OhmeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Ohme EV Charger."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @callback
    def _async_get_entry(self, data: dict[str, Any]) -> FlowResult:
        return self.async_create_entry(
            title=data["id"],
            data={
                "CHARGER_ID": data["id"],
                CONF_APIKEY: data[CONF_APIKEY],
                CONF_USERNAME: data[CONF_USERNAME],
                CONF_PASSWORD: data[CONF_PASSWORD],
            },
        )

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""

        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        if user_input is not None:
            charger_id = await self._test_credentials(
                user_input[CONF_APIKEY],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            if charger_id is not None:
                user_input["id"] = charger_id
                await self.async_set_unique_id(charger_id)
                return self._async_get_entry(user_input)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def _test_credentials(self, api_key, username, password) -> str:
        """Return true if credentials is valid."""
        _LOGGER.debug("Test Ohme API credentials")
        conn = OhmeAuth(api_key, username)
        try:
            await conn.start_auth(password)
            charger = OhmeCharger(conn)
            await charger.refresh()
            return charger.id
        except TimeoutException:
            _LOGGER.error("Timeout when communicating with Ohme API servers")
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error(
                "".join(traceback.format_exception(ex, value=ex, tb=ex.__traceback__))
            )
        return None
