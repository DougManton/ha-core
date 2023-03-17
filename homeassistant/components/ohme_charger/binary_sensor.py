"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_COORDINATOR, DATA_INFO
from .entity import OhmeChargerEntity
from .OhmeCharger import OhmeCharger
from . import OhmeDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ohme EV Charger sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        OhmeEVCharging(hass, coordinator, charger)
        for charger in hass.data[DOMAIN][config_entry.entry_id]["chargers"]
    )


class OhmeEVCharging(OhmeChargerEntity, BinarySensorEntity):
    """Ohme EV Smart Charger Data"""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        """Initialize charging entity."""
        super().__init__(hass, coordinator, charger)
        self.type = "charging"
        self._attr_icon = "mdi:ev-station"
        self._attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self) -> bool:
        """Return the charge status."""
        return self._device.charge_status == "SMART_CHARGE"
