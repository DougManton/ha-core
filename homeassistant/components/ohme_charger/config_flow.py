"""Config flow for Ohme Smart EV Charger integration."""
from __future__ import annotations

import logging
import traceback

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from . import SCAN_INTERVAL
from .OhmeAuth import OhmeAuth
from .OhmeCharger import OhmeCharger
from .const import CONF_APIKEY, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME, DOMAIN
from .exceptions import TimeoutException

_LOGGER: logging.Logger = logging.getLogger(__package__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("api_key"): str,
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


class OhmeFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Ohme EV Charger."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize."""
        self._errors: dict[str, str] = {}

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            err, client = await self._test_credentials(
                user_input[CONF_APIKEY],
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
            )
            if client:
                return self.async_create_entry(
                    title=client.session["chargeDevice"]["modelTypeDisplayName"],
                    data=user_input,
                )
            self._errors["base"] = err

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OhmeOptionsFlowHandler:
        """Get the options flow for this handler."""
        return OhmeOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        defaults = user_input or {CONF_APIKEY: "", CONF_USERNAME: "", CONF_PASSWORD: ""}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_APIKEY, default=defaults[CONF_APIKEY]): str,
                    vol.Required(CONF_USERNAME, default=defaults[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=defaults[CONF_PASSWORD]): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, api_key, username, password):
        """Return true if credentials is valid."""
        _LOGGER.debug("Test Ohme API credentials")
        conn = OhmeAuth(api_key, username)
        try:
            await conn.start_auth(password)
            charger = OhmeCharger(conn)
            await charger.refresh()
            return None, charger
        except TimeoutException:
            _LOGGER.error("Timeout when communicating with Ohme API servers")
            error = "connection_timeout"
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error(
                "".join(traceback.format_exception(ex, value=ex, tb=ex.__traceback__))
            )
            error = "connection"
        return error, None


class OhmeOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for myenergi."""

    def __init__(self, config_entry) -> None:
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input=None
    ) -> FlowResult:  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, SCAN_INTERVAL.total_seconds()
        )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=scan_interval): int,
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get("API " + CONF_USERNAME), data=self.options
        )
