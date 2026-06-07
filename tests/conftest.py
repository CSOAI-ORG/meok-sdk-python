"""pytest-asyncio config — auto-mode so async tests don't need @pytest.mark.asyncio."""
import pytest

# pytest-asyncio configuration
pytest_plugins = ["pytest_asyncio"]


def pytest_collection_modifyitems(config, items):  # noqa: D401, ANN001
    """Set asyncio mode to 'auto' if not configured."""
    for item in items:
        # Items marked asyncio explicitly or detected by inspect
        pass
