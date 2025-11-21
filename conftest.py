import pytest
from utils.data_reader import load_config

def pytest_collection_modifyitems(config, items):
    # Allow flag-based skipping via config file
    cfg = load_config()
    flags = cfg.get("test_flags", {})
    mapping = {
        "functional": "functional",
        "ui": "ui",
        "security": "security",
        "regression": "regression",
    }
    for marker, key in mapping.items():
        if not flags.get(key, True):
            skip_marker = pytest.mark.skip(reason=f"disabled by config: {key}")
            for item in items:
                if item.get_closest_marker(marker):
                    item.add_marker(skip_marker)
