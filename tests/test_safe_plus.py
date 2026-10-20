"""An i-soft SAFE+ set up end to end, against what a real one answers.

The payloads are those of an i-soft SAFE+ on device software 3.02. It answers
the write-only commands 3E, 3F, 40 and 41 with an empty payload, and command
69 and the scene commands with 400.
"""

import re

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.judo_rest_api.const import CONST
from custom_components.judo_rest_api.restobject import statistics_day

BASE = "http://192.0.2.10:80/api/rest/"
DAY = "0000000a00000000000000930000000000000034000000440000005400000043"

SAFE_PLUS = {
    "FF00": "33",
    "0600": "87230300",
    "0100": "6e0203",
    "5100": "0600",
    "5700": "15",
    "5600": "c2332c00",
    "2800": "aafe1a00",
    "2900": "6e711100",
    "5800": "2b34392037313935203639323531372020",
    "2500": "0F113608",
    "0E00": "6003b255",
    # Set to degrees eH here, so that adding instead of setting shows.
    "2300": "01",
}


def unique_id(key: str) -> str:
    """Return the unique id of an entity of the system device."""
    return f"{CONST.DOMAIN}_dev_system_{key}"


@pytest.fixture
def device(aioclient_mock):
    """Answer like an i-soft SAFE+."""
    for command, data in SAFE_PLUS.items():
        aioclient_mock.get(BASE + command, json={"data": data})
    aioclient_mock.get(
        BASE + "FB00" + statistics_day(dt_util.now().date()), json={"data": DAY}
    )
    for command in ("6900", "3700", "2400", "3E00", "3F00", "4000", "4100"):
        aioclient_mock.get(BASE + command, status=400)
    return aioclient_mock


def sent(aioclient_mock, prefix: str) -> list[str]:
    """Return the commands sent that start with a command code.

    Upper case: numbers go out in lower case hex, as they always have, and
    the device takes either.
    """
    commands = [
        url.path.removeprefix("/api/rest/").upper()
        for _method, url, _data, _headers in aioclient_mock.mock_calls
    ]
    return [command for command in commands if command.startswith(prefix)]


async def setup(hass: HomeAssistant, aioclient_mock) -> MockConfigEntry:
    """Set up one config entry for the device."""
    entry = MockConfigEntry(
        domain=CONST.DOMAIN,
        version=2,
        unique_id="192.0.2.10",
        data={
            "host": "192.0.2.10",
            "port": 80,
            "username": "admin",
            "password": "secret",
            "Device-Postfix": "",
            "scan_interval": "60",
        },
    )
    entry.add_to_hass(hass)
    # Writes answer with an empty payload, like the device.
    aioclient_mock.get(
        re.compile(r"/api/rest/(2400|3E00|3F00|4000|4100)[0-9A-Fa-f]+$"),
        json={"data": ""},
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def entity_id(hass: HomeAssistant, platform: str, key: str) -> str | None:
    """Look an entity up by its unique id."""
    return er.async_get(hass).async_get_entity_id(platform, CONST.DOMAIN, unique_id(key))


async def test_entities(hass: HomeAssistant, custom_integration, device) -> None:
    """A SAFE+ gets its own entities and none of the PRO's."""
    await setup(hass, device)

    for platform, key in [
        ("select", "water_scene"),
        ("select", "water_scene_duration"),
        ("sensor", "water_flow"),
        ("sensor", "water_temperature"),
    ]:
        assert entity_id(hass, platform, key) is None, key
    assert not sent(device, "69")
    assert not sent(device, "37")

    def state(platform, key):
        return hass.states.get(entity_id(hass, platform, key))

    assert state("sensor", "device_number").state == "205703"
    assert state("sensor", "install_date").state == "2021-01-17"
    assert float(state("sensor", "operating_time").state) == pytest.approx(50465.25)
    assert state("sensor", "software_version").state == "3.02n"
    assert state("select", "hardness_unit").state == "unit_eh"

    today = state("sensor", "water_today")
    assert today.state == "428"
    assert today.attributes["06:00-09:00"] == 147

    # Write-only: unknown, not unavailable, until set from here.
    assert state("select", "vacation_mode").state == "unknown"
    assert state("switch", "micro_leakage_close").state == "unknown"
    assert state("number", "max_extraction_volume").state == "unknown"


async def test_select_sets_instead_of_adding(
    hass: HomeAssistant, custom_integration, device
) -> None:
    """Picking ppm (4) while eH (1) is set sends 4, not 5."""
    await setup(hass, device)
    await hass.services.async_call(
        "select",
        "select_option",
        {"entity_id": entity_id(hass, "select", "hardness_unit"), "option": "unit_ppm"},
        blocking=True,
    )
    assert sent(device, "2400") == ["240004"]


async def test_limits(hass: HomeAssistant, custom_integration, device) -> None:
    """3F takes litres little-endian, as in the document's 3F00C409."""
    await setup(hass, device)
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id(hass, "number", "max_extraction_volume"), "value": 2500},
        blocking=True,
    )
    assert sent(device, "3F00") == ["3F00C409"]
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id(hass, "number", "max_extraction_duration"), "value": 40},
        blocking=True,
    )
    assert sent(device, "3E00") == ["3E0028"]

    # The value written survives the next scan.
    coordinator = hass.config_entries.async_entries(CONST.DOMAIN)[0].runtime_data.coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    number = hass.states.get(entity_id(hass, "number", "max_extraction_volume"))
    assert float(number.state) == 2500
    assert number.attributes.get("assumed_state") is True


async def test_holiday_mode_keeps_leakage_settings(
    hass: HomeAssistant, custom_integration, device
) -> None:
    """Command 41 is only sent once every part of it is known."""
    await setup(hass, device)

    async def turn(key, service):
        await hass.services.async_call(
            "switch", service, {"entity_id": entity_id(hass, "switch", key)}, blocking=True
        )

    async def holiday(option):
        await hass.services.async_call(
            "select",
            "select_option",
            {"entity_id": entity_id(hass, "select", "vacation_mode"), "option": option},
            blocking=True,
        )

    # Nothing known yet: holiday mode must not go out with guessed bits.
    with pytest.raises(HomeAssistantError, match="not sent"):
        await holiday("vacation_u1")
    assert not sent(device, "41")

    # The settings of the app: test active, close on micro leakage, protection on.
    with pytest.raises(HomeAssistantError, match="not sent"):
        await turn("micro_leakage_close", "turn_on")
    with pytest.raises(HomeAssistantError, match="not sent"):
        await turn("micro_leakage_auto_test", "turn_on")
    assert not sent(device, "41")

    # The last part completes the byte: U1 (0x03) + bit 5 + bit 6.
    await turn("leakage_protection_off", "turn_off")
    assert sent(device, "41") == ["410063"]

    await holiday("vacation_off")
    assert sent(device, "41")[-1] == "410060"

    await turn("micro_leakage_auto_test", "turn_off")
    assert sent(device, "41")[-1] == "410020"

    state = hass.states.get(entity_id(hass, "select", "vacation_mode"))
    assert state.state == "vacation_off"
    assert hass.states.get(entity_id(hass, "switch", "micro_leakage_close")).state == "on"


async def test_scene_entities_of_1_3_are_removed(
    hass: HomeAssistant, custom_integration, device
) -> None:
    """Entities 1.3 created on a SAFE+ for the PRO's commands are dropped."""
    registry = er.async_get(hass)
    entry = MockConfigEntry(
        domain=CONST.DOMAIN,
        version=2,
        unique_id="192.0.2.10",
        data={
            "host": "192.0.2.10",
            "port": 80,
            "username": "admin",
            "password": "secret",
            "Device-Postfix": "",
            "scan_interval": "60",
        },
    )
    entry.add_to_hass(hass)
    registry.async_get_or_create(
        "select", CONST.DOMAIN, unique_id("water_scene"), config_entry=entry
    )
    registry.async_get_or_create(
        "sensor", CONST.DOMAIN, unique_id("water_total"), config_entry=entry
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entity_id(hass, "select", "water_scene") is None
    assert entity_id(hass, "sensor", "water_total") is not None


@pytest.mark.parametrize(
    ("devicetype", "polled", "never"),
    [
        # A PRO keeps what 1.3 gave it, command 69 included.
        ("58", {"6900", "5100", "2800"}, {"2300", "FB00"}),
        # On a ZEWA i-SAFE 5100 closes the valve and 5700 starts the holiday
        # mode: nothing but the info commands may be sent.
        ("44", {"FF00", "0600", "0100"}, {"5100", "5700", "5800", "5600", "2800"}),
    ],
)
async def test_other_families(
    hass: HomeAssistant, custom_integration, aioclient_mock, devicetype, polled, never
) -> None:
    """Each family is polled for its own commands only."""
    aioclient_mock.get(re.compile(r"/api/rest/FF00$"), json={"data": devicetype})
    aioclient_mock.get(re.compile(r"/api/rest/(?!FF00)[0-9A-F]+$"), json={"data": "00" * 16})
    await setup(hass, aioclient_mock)
    commands = {command[:4] for command in sent(aioclient_mock, "")}
    assert polled <= commands
    assert not commands & never
