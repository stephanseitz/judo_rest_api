"""Which device gets which items."""

import pytest

from custom_components.judo_rest_api.const import FAMILIES, TYPES, family_of
from custom_components.judo_rest_api.jdconst import DEVICELISTS

ALL_ITEMS = [item for items in DEVICELISTS for item in items]
ALL_FAMILIES = [
    FAMILIES.I_SOFT,
    FAMILIES.SAFE_PLUS,
    FAMILIES.PRO,
    FAMILIES.SOFTWELL,
    FAMILIES.OTHER,
]


def items_of(family: str):
    """Return the items a device of this family gets."""
    return [item for item in ALL_ITEMS if item.supports(family)]


@pytest.mark.parametrize(
    ("devicetype", "family"),
    [
        ("33", FAMILIES.SAFE_PLUS),
        ("57", FAMILIES.SAFE_PLUS),
        ("67", FAMILIES.SAFE_PLUS),
        ("58", FAMILIES.PRO),
        ("4b", FAMILIES.PRO),
        ("32", FAMILIES.I_SOFT),
        ("34", FAMILIES.SOFTWELL),
        # Softener types the document does not list keep the i-soft items.
        ("56", FAMILIES.I_SOFT),
        ("44", FAMILIES.OTHER),
        ("3C", FAMILIES.OTHER),
        ("41", FAMILIES.OTHER),
        ("EE", FAMILIES.OTHER),
        ("", FAMILIES.OTHER),
        (None, FAMILIES.OTHER),
        ("zz", FAMILIES.OTHER),
    ],
)
def test_family_of(devicetype, family):
    """Map device types to families."""
    assert family_of(devicetype) == family


@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_one_item_per_entity(family):
    """Two items of one family must never produce the same unique id."""
    keys = [(item.device, item.translation_key) for item in items_of(family)]
    assert len(keys) == len(set(keys))


def test_safe_plus_items():
    """The SAFE+ gets the holiday byte, but nothing of command 69 or 36/37."""
    reads = {item.address_read for item in items_of(FAMILIES.SAFE_PLUS)}
    writes = {item.address_write for item in items_of(FAMILIES.SAFE_PLUS)}
    assert "6900" not in reads
    assert "3600" not in writes
    assert {"4100", "3E00", "3F00", "4000", "2400"} <= writes
    assert {"2300", "FB00"} <= reads
    # The write-only commands must never be polled: they answer empty.
    assert not reads & {"3E00", "3F00", "4000", "4100"}


def test_pro_items_unchanged():
    """The PRO keeps scenes and command 69 and gets nothing new."""
    keys = {item.translation_key for item in items_of(FAMILIES.PRO)}
    assert {"water_scene", "water_scene_duration", "water_flow", "water_temperature"} <= keys
    assert not keys & {"vacation_mode", "hardness_unit", "water_today", "max_flow_rate"}


def test_other_devices_only_get_info():
    """On a ZEWA 5100 closes the valve and 5700 starts the holiday mode."""
    items = items_of(FAMILIES.OTHER)
    assert {item.address_read for item in items} == {"FF00", "0600", "0100"}
    assert all(item.type == TYPES.SENSOR for item in items)


def test_softwell_has_no_controls():
    """SOFTwell documents neither salt nor hardness nor the valve."""
    commands = {
        command
        for item in items_of(FAMILIES.SOFTWELL)
        for command in (item.address_read, item.address_write)
    }
    assert not commands & {"5100", "5600", "5700", "2800", "3C00", "3D00", "350000"}
    assert {"2900", "2500", "0E00", "FB00"} <= commands
