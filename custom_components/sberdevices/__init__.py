"""The SberDevices integration."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .core.auth import SberAuthClient
from .core.coordinator import SberDataUpdateCoordinator
from .core.gateway import SberHomeGatewayClient
from .core.runtime import SberConfigEntry, SberRuntimeData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: SberConfigEntry) -> bool:
    """Set up SberDevices from a config entry."""

    auth_client = SberAuthClient(token=entry.data["token"])
    gateway_client = SberHomeGatewayClient(auth_client)
    coordinator = SberDataUpdateCoordinator(hass, gateway_client)
    entry.runtime_data = SberRuntimeData(
        auth_client=auth_client,
        gateway_client=gateway_client,
        coordinator=coordinator,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
        for device in coordinator.data.values():
            _LOGGER.info(
                "Discovered %s image_set_type=%s",
                device["name"]["name"],
                device["image_set_type"],
            )
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await entry.runtime_data.async_close()
        raise

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SberConfigEntry) -> bool:
    """Unload a config entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False

    await entry.runtime_data.async_close()
    return True


__all__ = ["PLATFORMS", "async_setup_entry", "async_unload_entry"]
