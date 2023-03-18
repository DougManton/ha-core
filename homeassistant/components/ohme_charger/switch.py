"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
        OhmeEVCharger(hass, coordinator, charger)
        for charger in hass.data[DOMAIN][config_entry.entry_id]["chargers"]
    )


class OhmeEVCharger(OhmeChargerEntity, SwitchEntity):
    """Ohme EV Smart Charger Control"""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        """Initialize charging entity."""
        super().__init__(hass, coordinator, charger)
        self.type = "charger"
        self._attr_icon = "mdi:ev-station"

    @property
    def is_on(self) -> bool:
        """Return charging state."""
        return self._device.session["mode"] == "MAX_CHARGE"

    async def async_turn_on(self, **kwargs) -> None:
        """Send the on command."""
        await self._device.start_charge()
        await self.async_update_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Send the off command."""
        await self._device.stop_charge()
        await self.async_update_ha_state()
