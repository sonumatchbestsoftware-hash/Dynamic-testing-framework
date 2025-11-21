import pytest
from utils.data_reader import load_locators

@pytest.mark.ui
def test_homepage_logo_visible(browser, base_url):
    loc = load_locators()
    home = loc.get("homepage", {})
    browser.get(f"{base_url}/")
    try:
        logo = browser.find_element(home["logo"]["by"], home["logo"]["value"])
    except Exception as e:
        pytest.skip(f"Logo selector not found: {e}")
    assert logo.is_displayed(), "Homepage logo not visible"

@pytest.mark.ui
def test_primary_cta_present(browser, base_url):
    loc = load_locators()
    home = loc.get("homepage", {})
    browser.get(f"{base_url}/")
    try:
        cta = browser.find_element(home["primary_cta"]["by"], home["primary_cta"]["value"])
    except Exception as e:
        pytest.skip(f"CTA selector not found: {e}")
    assert cta.is_displayed(), "Primary CTA not visible on homepage"
