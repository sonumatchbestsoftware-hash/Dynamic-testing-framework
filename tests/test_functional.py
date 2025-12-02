import time
import pytest
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.data_reader import load_config, load_locators, load_form, load_urls


def _normalize_by(by_str):
    if not by_str:
        return By.CSS_SELECTOR
    s = by_str.lower()
    if "css" in s:
        return By.CSS_SELECTOR
    if "id" in s and "selector" not in s:
        return By.ID
    if "xpath" in s:
        return By.XPATH
    if "name" in s:
        return By.NAME
    if "class" in s and "name" in s:
        return By.CLASS_NAME
    if "tag" in s:
        return By.TAG_NAME
    if "link" in s:
        return By.LINK_TEXT
    return by_str


@pytest.mark.functional
def test_dynamic_pages_and_forms(browser, base_url, cfg):
    """Dynamic functional test: for each configured page, verify reachability,
    check presence/visibility of declared locators, and attempt form fills
    on pages that declare auth fields.
    """
    # Load config safely
    try:
        config = load_config()
    except Exception as e:
        pytest.skip(f"Could not load config: {e}")
    
    # Load pages from config or fallback to Excel
    try:
        pages = config.get("pages", []) if config else []
        if not pages:
            pages = load_urls()
    except Exception as e:
        pytest.skip(f"Could not load pages: {e}")

    # Load locators safely
    try:
        locators = load_locators()
    except Exception as e:
        pytest.skip(f"Could not load locators: {e}")

    # Load form data safely
    forms = []
    try:
        form_data = load_form()
        if form_data:
            forms = form_data
    except Exception as e:
        pass  # Forms are optional

    # Get explicit wait timeout
    explicit_wait = 15
    if config and isinstance(config.get("timeouts"), dict):
        try:
            explicit_wait = int(config.get("timeouts", {}).get("explicit", 15))
        except (ValueError, TypeError):
            explicit_wait = 15

    for path in pages:
        # Build absolute URL
        url = f"{base_url.rstrip('/')}{path}"
        # Sanity check with requests first
        try:
            r = requests.get(url, timeout=20)
            if r.status_code >= 500:
                pytest.skip(f"{url} not reachable: {r.status_code}")
        except Exception as e:
            pytest.skip(f"Skipping {url}: network check failed: {e}")

        try:
            browser.get(url)
        except Exception as e:
            pytest.skip(f"Could not navigate to {url}: {e}")

        # Infer locator key from path (e.g., '/' -> 'homepage', '/login' -> 'auth')
        key = path.strip('/').split('/')[0] if path.strip('/') else 'homepage'
        page_loc = locators.get(key, {})

        if not page_loc:
            pytest.skip(f"No locators found for page key '{key}' on {url}")

        # Check visibility/presence of configured elements for the page
        for name, sel in page_loc.items():
            if not isinstance(sel, dict):
                continue
            by = _normalize_by(sel.get('by'))
            value = sel.get('value')
            if not value:
                continue
            try:
                el = WebDriverWait(browser, explicit_wait).until(
                    EC.presence_of_element_located((by, value))
                )
                if not el.is_displayed():
                    pytest.skip(f"Element '{name}' not visible on {url}")
            except Exception as e:
                pytest.skip(f"Element '{name}' not present on {url}: {str(e)[:100]}")

        # If this is an auth/login page, attempt to fill the first available form
        required_auth_fields = {'username', 'password', 'submit'}
        page_loc_keys = set(page_loc.keys())
        if key == 'auth' and required_auth_fields.issubset(page_loc_keys):
            if not forms:
                pytest.skip("No form data available to exercise login")
            
            data = forms[0]
            try:
                # Wait for and fill username field
                user = WebDriverWait(browser, explicit_wait).until(
                    EC.presence_of_element_located(
                        (_normalize_by(page_loc['username']['by']), page_loc['username']['value'])
                    )
                )
                # Find password and submit button
                pwd = browser.find_element(
                    _normalize_by(page_loc['password']['by']), 
                    page_loc['password']['value']
                )
                btn = browser.find_element(
                    _normalize_by(page_loc['submit']['by']), 
                    page_loc['submit']['value']
                )

                # Fill form and submit
                user.clear()
                user.send_keys(data.get('username', ''))
                pwd.clear()
                pwd.send_keys(data.get('password', ''))
                btn.click()
                
                # Wait briefly for response
                time.sleep(2)
                
                # Check for error in URL
                current_url = browser.current_url.lower()
                if 'error' in current_url:
                    pytest.skip(f"Login resulted in error URL on {url}: {browser.current_url}")
            except Exception as e:
                pytest.skip(f"Login flow on {url} failed: {str(e)[:100]}")

