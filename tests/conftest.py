"""Fixtures for the Judo REST API tests."""

import pytest


@pytest.fixture
def custom_integration(enable_custom_integrations):
    """Let HA load custom_components/judo_rest_api."""
    yield
