"""Setting up and reconfiguring an entry."""

import re
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.judo_rest_api.const import CONST

USER_INPUT = {
    "host": "192.0.2.10",
    "port": 80,
    "username": "admin",
    "password": "secret",
    "Device-Postfix": "",
    "scan_interval": 60,
}
# The reconfigure form has no device postfix: it is part of every unique id.
RECONFIGURE_INPUT = {key: value for key, value in USER_INPUT.items() if key != "Device-Postfix"}


def entry_for(host: str) -> MockConfigEntry:
    """Return a config entry for a device at this host."""
    return MockConfigEntry(
        domain=CONST.DOMAIN,
        version=2,
        unique_id=host,
        data={**USER_INPUT, "host": host, "scan_interval": "60"},
    )


async def test_refused_password(
    hass: HomeAssistant, custom_integration, aioclient_mock
) -> None:
    """A 401 says the credentials are wrong, not that the device is away."""
    aioclient_mock.get(re.compile(r"/api/rest/FF00$"), status=401)
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_unreachable(
    hass: HomeAssistant, custom_integration, aioclient_mock
) -> None:
    """A device that does not answer is a connection failure."""
    aioclient_mock.get(re.compile(r"/api/rest/FF00$"), status=503)
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["errors"] == {"base": "cannot_connect"}


@pytest.fixture
def no_setup():
    """Keep the entry from being loaded after reconfiguring it."""
    with patch(
        "custom_components.judo_rest_api.async_setup_entry", return_value=True
    ):
        yield


async def test_reconfigure_rejects_postfix(
    hass: HomeAssistant, custom_integration, aioclient_mock, no_setup
) -> None:
    """Changing the postfix used to orphan every entity and its history."""
    entry = entry_for("192.0.2.10")
    entry.add_to_hass(hass)
    result = await entry.start_reconfigure_flow(hass)
    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {**RECONFIGURE_INPUT, "Device-Postfix": "b"}
        )


async def test_reconfigure_moves_unique_id(
    hass: HomeAssistant, custom_integration, aioclient_mock, no_setup
) -> None:
    """A new address becomes the entry's unique id; the postfix stays put."""
    aioclient_mock.get(re.compile(r"/api/rest/FF00$"), json={"data": "33"})
    entry = entry_for("192.0.2.10")
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    assert "Device-Postfix" not in result["data_schema"].schema
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**RECONFIGURE_INPUT, "host": "192.0.2.20"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.unique_id == "192.0.2.20"
    assert entry.data["host"] == "192.0.2.20"


async def test_reconfigure_onto_another_entry(
    hass: HomeAssistant, custom_integration, aioclient_mock, no_setup
) -> None:
    """Two entries must not end up polling the same device."""
    aioclient_mock.get(re.compile(r"/api/rest/FF00$"), json={"data": "33"})
    entry = entry_for("192.0.2.10")
    entry.add_to_hass(hass)
    entry_for("192.0.2.20").add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**RECONFIGURE_INPUT, "host": "192.0.2.20"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"host": "host_in_use"}
    assert entry.unique_id == "192.0.2.10"
