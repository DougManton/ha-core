"""OhmeChargerEntity class"""
import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import OhmeDataUpdateCoordinator
from .OhmeCharger import OhmeCharger

from .const import DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)


class OhmeChargerEntity(CoordinatorEntity):
    """Coordinates the charging device"""

    def __init__(
        self,
        coordinator: OhmeDataUpdateCoordinator,
        device: OhmeCharger,
        config_entry,
    ) -> None:
        super().__init__(coordinator)
        self.device = device
        self.coordinator = coordinator
        self.config_entry = config_entry
        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, self.device.session["chargeDevice"]["id"])},
            manufacturer="Ohme",
            model=self.device.session["chargeDevice"][
                "modelTypeDisplayName"
            ].capitalize(),
            name=self.device.session["chargeDevice"]["modelTypeDisplayName"],
            sw_version=self.device.session["chargeDevice"]["firmwareVersionLabel"],
        )

    async def start_charge(self) -> None:
        """Start charge"""
        _LOGGER.debug("Start charge called")
        await self.device.start_charge()
        self.schedule_update_ha_state()

    async def stop_charge(self) -> None:
        """Stop charge"""
        _LOGGER.debug("Stop charge called")
        await self.device.stop_charge()
        self.schedule_update_ha_state()

    async def pause_charge(self) -> None:
        """Pause charge"""
        _LOGGER.debug("Pause charge called")
        await self.device.pause_charge()
        self.schedule_update_ha_state()

    async def resume_charge(self) -> None:
        """Resume charge"""
        _LOGGER.debug("Resume charge called")
        await self.device.resume_charge()
        self.schedule_update_ha_state()

    async def switch_amps(self, amps: int) -> None:
        """Set charge amperage"""
        _LOGGER.debug("Set amps called %s", amps)
        await self.device.switch_amps(amps)
        self.schedule_update_ha_state()

    @property
    def charge_status(self) -> str:
        """Get charge status"""
        _LOGGER.debug("Get charge status called")
        return self.device.charge_status()

    @callback
    def _handle_coordinator_update(self) -> None:
        self.device = self.coordinator.data[self.device.id]
        super()._handle_coordinator_update()
