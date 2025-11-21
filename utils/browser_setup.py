import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from .data_reader import load_config

@pytest.fixture(scope="session")
def cfg():
    return load_config()

@pytest.fixture(scope="session")
def base_url(cfg):
    return cfg.get("base_url").rstrip("/")

@pytest.fixture(scope="session")
def browser(cfg):
    # Lazily set up Chrome with or without UI depending on config
    options = ChromeOptions()
    if cfg.get("headless", True) or os.getenv("HEADLESS", "1") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
    driver.implicitly_wait(int(cfg.get("timeouts", {}).get("implicit", 5)))
    yield driver
    driver.quit()
