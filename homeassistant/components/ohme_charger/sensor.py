"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    POWER_KILO_WATT,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_COORDINATOR
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
        OhmeEVCurrentPower(hass, coordinator, charger)
        for charger in hass.data[DOMAIN][config_entry.entry_id]["chargers"]
    )


class OhmeEVCurrentPower(OhmeChargerEntity, SensorEntity):
    """Ohme EV Smart Charger Data"""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        """Initialize charging entity."""
        super().__init__(hass, coordinator, charger)
        self.type = "charger power"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = POWER_KILO_WATT

    @property
    def native_min_value(self) -> int:
        """Return min charging power."""
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, int]:
        """Return device state attributes."""
        return {
            "charger_volts": self._device.current_voltage,
            "charger_amps": self._device.current_amps,
        }

    @property
    def native_value(self) -> float:
        """Return the charge power in kW."""
        return self._device.current_power / 1000
