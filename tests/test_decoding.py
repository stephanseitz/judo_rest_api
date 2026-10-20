"""Decoding against payloads captured from real devices.

i-soft SAFE+ on device software 3.02, compared with what the Judo app shows
for the same device: device number 205703, commissioned 17.01.2021, 2102
operating days on 20.10.2026, hardness unit dH, and for 20.10.2026 the
3-hour buckets 10 l, 0, 147 l, 0, 52 l. The i-soft PRO payloads are the ones
recorded in tools/README.md.
"""

from datetime import date

import pytest

from custom_components.judo_rest_api.const import FAMILIES
from custom_components.judo_rest_api.jdconst import DEVICELISTS
from custom_components.judo_rest_api.restobject import (
    JudoDecodeError,
    decode_day_statistics,
    decode_item,
    statistics_day,
)

ALL_ITEMS = [item for items in DEVICELISTS for item in items]

SAFE_PLUS_DAY = "0000000a00000000000000930000000000000034000000440000005400000043"


def item_for(family: str, translation_key: str):
    """Return the item a device of this family gets for a translation key."""
    matches = [
        item
        for item in ALL_ITEMS
        if item.translation_key == translation_key and item.supports(family)
    ]
    assert len(matches) == 1, f"{translation_key} for {family}: {matches}"
    return matches[0]


def decode(family: str, translation_key: str, raw: str):
    """Decode a payload the way a device of this family is served."""
    item = item_for(family, translation_key)
    divider = (item.params or {}).get("divider", 1)
    return decode_item(item, raw, divider)


@pytest.mark.parametrize(
    ("translation_key", "raw", "expected"),
    [
        ("device_type", "33", "i_soft_safe_plus"),
        ("device_number", "87230300", "205703"),
        ("software_version", "6e0203", "3.02n"),
        # 15 min, 17 h, 2102 days
        ("operating_time", "0F113608", 2102 * 24 + 17 + 15 / 60),
        ("install_date", "6003b255", date(2021, 1, 17)),
        ("hardness_unit", "00", "unit_dh"),
        ("water_hardeness", "0600", 6),
        ("water_today", SAFE_PLUS_DAY, 10 + 147 + 52 + 68 + 84 + 67),
    ],
)
def test_safe_plus(translation_key, raw, expected):
    """The SAFE+ reads little-endian counters and unix time."""
    assert decode(FAMILIES.SAFE_PLUS, translation_key, raw) == expected


@pytest.mark.parametrize(
    ("translation_key", "raw", "expected"),
    [
        ("device_number", "24146BA8", "605318056"),
        ("software_version", "110401", "1.4.17"),
        ("operating_time", "0E150209", 521 * 24 + 21 + 14 / 60),
        ("install_date", "0d0507e9", date(2025, 5, 13)),
    ],
)
def test_pro_unchanged(translation_key, raw, expected):
    """The PRO family keeps its big-endian and day/month/year layout."""
    assert decode(FAMILIES.PRO, translation_key, raw) == expected


def test_day_statistics_buckets():
    """FB holds eight big-endian 4 byte values, 00:00-03:00 first."""
    assert decode_day_statistics(SAFE_PLUS_DAY) == [10, 0, 147, 0, 52, 68, 84, 67]


def test_day_statistics_too_short():
    """A short answer is an error, not a smaller total."""
    with pytest.raises(JudoDecodeError):
        decode(FAMILIES.SAFE_PLUS, "water_today", SAFE_PLUS_DAY[:-8])


def test_statistics_day():
    """The date argument puts the year big-endian, as in FB000D0807E7."""
    assert statistics_day(date(2023, 8, 13)) == "0D0807E7"
    assert statistics_day(date(2026, 10, 20)) == "140A07EA"


def test_timestamp_zero_is_no_date():
    """A device without a commissioning date must not report 1970."""
    with pytest.raises(JudoDecodeError):
        decode(FAMILIES.SAFE_PLUS, "install_date", "00000000")
