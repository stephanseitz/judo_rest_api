"""Setting uop my sensor entities."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES
from .entity_helpers import build_entity_list

_LOGGER: logging.Logger = logging.getLogger(name=__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    _useless = hass
    # start with an empty list of entries
    entries = []

    # we create one communicator per integration only for better performance and to allow dynamic parameters
    coordinator = config_entry.runtime_data.coordinator

    # Only the items the device's family knows, as chosen by the coordinator.
    for item_type in (TYPES.NUMBER_RO, TYPES.SENSOR):
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            rest_items=coordinator.items,
            item_type=item_type,
            coordinator=coordinator,
        )

    async_add_entities(entries)
