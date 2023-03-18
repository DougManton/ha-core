"""OhmeChargerEntity class"""
import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from . import OhmeDataUpdateCoordinator

from .const import DOMAIN
from .OhmeCharger import OhmeCharger

_LOGGER: logging.Logger = logging.getLogger(__package__)


class OhmeChargerEntity(CoordinatorEntity[OhmeDataUpdateCoordinator]):
    """Coordinates the charging device"""

    _attr_has_entity_name = True

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: OhmeDataUpdateCoordinator,
        charger: OhmeCharger,
    ) -> None:
        super().__init__(coordinator)
        self._device = charger
        self._coordinator = coordinator
        self.hass = hass
        self.type = None
        self._enabled_by_default: bool = True
        self._memorized_unique_id = None
        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, charger.id)},
            manufacturer="Ohme",
            name=charger.id,
            model=charger.model,
        )

    async def update_controller(self, *, blocking: bool = True) -> None:
        """Get the latest data from Ohme.
        This does a controller update then a coordinator update.
        The coordinator triggers a call to the refresh function.
        Setting the blocking param to False will create a background task for the update.
        """

        if blocking is False:
            await self.hass.async_create_task(self.update_controller())
            return

        await self._coordinator.controller.update(self._device.id)
        await self._coordinator.async_refresh()

    def refresh(self) -> None:
        """Refresh the device data.
        This is called by the DataUpdateCoodinator when new data is available.
        This assumes the controller has already been updated. This should be
        called by inherited classes so the overall device information is updated.
        """
        self.async_write_ha_state()

    @property
    def name(self) -> str:
        """Return device name."""
        return self.type.capitalize()

    @property
    def unique_id(self) -> str:
        """Return unique id for car entity."""
        if not self._memorized_unique_id:
            self._memorized_unique_id = slugify(f"{self._device.id} {self.type}")
        return self._memorized_unique_id

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Set entity registry to default."""
        return self._enabled_by_default

    async def async_added_to_hass(self) -> None:
        """Register state update callback."""
        self.async_on_remove(self.coordinator.async_add_listener(self.refresh))
