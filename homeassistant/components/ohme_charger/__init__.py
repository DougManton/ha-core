"""The Ohme Smart EV Charger integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import homeassistant.util.dt as dt_util

from .OhmeAuth import OhmeAuth
from .OhmeCharger import OhmeCharger
from .const import (
    CONF_APIKEY,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    DATA_COORDINATOR,
    DATA_INFO,
)

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER: logging.Logger = logging.getLogger(__package__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ohme Smart EV Charger from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    api_key = entry.data.get(CONF_APIKEY)

    conn = OhmeAuth(str(api_key), str(username))
    await conn.start_auth(str(password))
    charger = OhmeCharger(conn)

    coordinator = OhmeDataUpdateCoordinator(hass, charger)
    hass.data.setdefault(DOMAIN, {})
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_INFO: charger.id,
    }
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


class OhmeDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: OhmeCharger) -> None:
        """Initialize."""
        self._client = client

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Update data via library."""
        today = dt_util.now()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        utc_today = dt_util.as_utc(today)
        _LOGGER.debug(
            "Refresh history local start of day in UTC %s %s",
            utc_today,
            utc_today.tzinfo,
        )
        try:
            await self._client.refresh()
        except Exception as exception:
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
