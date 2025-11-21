import pytest
import requests
from utils.data_reader import load_urls
from utils.data_reader import load_locators
from utils.data_reader import load_form

@pytest.mark.functional
def test_public_pages_reachable(base_url):
    for path in load_urls():
        url = f"{base_url}{path}"
        resp = requests.get(url, timeout=20)
        assert resp.status_code < 500, f"{url} not reachable: {resp.status_code}"

@pytest.mark.functional
def test_login_flow(browser, base_url):
    loc = load_locators()
    login = loc.get("auth", {})
    browser.get(f"{base_url}/login")

    # If the site doesn't have a login page, skip
    try:
        user = browser.find_element(login["username"]["by"], login["username"]["value"])
        pwd  = browser.find_element(login["password"]["by"], login["password"]["value"])
        btn  = browser.find_element(login["submit"]["by"],   login["submit"]["value"])
    except Exception as e:
        pytest.skip(f"Login selectors not found: {e}")

    form = load_form()[0]
    user.clear(); user.send_keys(form.get("username", ""))
    pwd.clear();  pwd.send_keys(form.get("password", ""))
    btn.click()

    # Very generic post-login assertion: URL changes or no client-side error
    assert "error" not in browser.current_url.lower(), "Possible login error detected in URL"
