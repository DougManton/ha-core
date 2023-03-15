"""Sensor platform for Ohme EV Charger."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, DATA_COORDINATOR, DATA_INFO
from .entity import OhmeChargerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Ohme EV Charger sensor platform."""
    info = hass.data[DOMAIN][config_entry.entry_id][DATA_INFO]
    coordinator = hass.data[DOMAIN][config_entry.entry_id][DATA_COORDINATOR]
    async_add_entities(
        OhmeEVCharger(coordinator, charger_id, info) for charger_id in coordinator.data
    )


class OhmeEVCharger(OhmeChargerEntity, SensorEntity):
    """Ohme EV Smart Charger Data"""

    _attr_has_entity_name = True
    entity_description = SensorEntityDescription(
        key="charge_status",
        entity_category=EntityCategory.CONFIG,
        name="Charge Status",
        icon="mdi:lightning-bolt",
    )

    @property
    def native_value(self) -> str:
        """Return the charge status string."""
        return self.charge_status or "UNKNOWN"
