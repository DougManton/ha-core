"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberMode,
)
from homeassistant.const import ELECTRIC_CURRENT_AMPERE
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_COORDINATOR
from .entity import OhmeChargerEntity
from .OhmeCharger import OhmeCharger
from . import OhmeDataUpdateCoordinator

import math


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ohme EV Charger sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        OhmeEVMaxAmps(hass, coordinator, charger)
        for charger in hass.data[DOMAIN][config_entry.entry_id]["chargers"]
    )


class OhmeEVMaxAmps(OhmeChargerEntity, NumberEntity):
    """Ohme EV Smart Charger Data"""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        """Initialize charging entity."""
        super().__init__(hass, coordinator, charger)
        self.type = "charging amps"
        self._attr_icon = "mdi:ev-station"
        self.attr_mode = NumberMode.AUTO

    @property
    def native_unit_of_measurement(self) -> str:
        """Return data type."""
        return ELECTRIC_CURRENT_AMPERE

    @property
    def native_min_value(self) -> int:
        """Return min amperage."""
        return 0

    @property
    def native_max_value(self) -> int:
        """Return max amperage."""
        return 48

    @property
    def native_value(self) -> float:
        """Return the charge status."""
        return math.floor(self._device.max_amps)

    async def async_set_native_value(self, value: float) -> None:
        """Update charging amps."""
        await self._device.switch_amps(math.floor(value))
        await self.async_update_ha_state()
