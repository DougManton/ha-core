"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_COORDINATOR
from .entity import OhmeChargerEntity
from .OhmeCharger import OhmeCharger
from . import OhmeDataUpdateCoordinator

import time


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ohme EV Charger sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        OhmeEVScheduledCharging(hass, coordinator, charger)
        for charger in hass.data[DOMAIN][config_entry.entry_id]["chargers"]
    )


class OhmeEVScheduledCharging(OhmeChargerEntity, BinarySensorEntity):
    """Representation of a Ohme car scheduled charging binary sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        """Initialize scheduled charging entity."""
        super().__init__(hass, coordinator, charger)
        self.type = "scheduled charging"
        self._attr_icon = "mdi:calendar-plus"
        self._attr_device_class = None

    @property
    def is_on(self) -> bool:
        """Return True if scheduled charging enabled."""
        if self._device.get_charge_times() != []:
            return True
        return False

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return device state attributes."""
        # pylint: disable=protected-access
        times = self._device.get_charge_times()
        return {
            "Next charge start": time.gmtime(times[0]),
            "Next charge end": time.gmtime(times[1]),
        }
