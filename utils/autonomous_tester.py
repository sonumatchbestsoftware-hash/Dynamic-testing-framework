"""
Autonomous Test Generator

Generates and executes test cases based on discovered elements and credentials.
Handles login flows, form submission, element validation, and comprehensive testing.
"""

import time
from typing import Dict, Optional, Tuple
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
import yaml
from loguru import logger


class AutonomousTestExecutor:
    """Executes automated tests on discovered elements with login capability."""

    def __init__(self, headless: bool = True, implicit_wait: int = 5, explicit_wait: int = 15):
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.explicit_wait = explicit_wait
        self.driver = None
        self.test_results = []

    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        options = ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")

        driver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(service=ChromeService(driver_path), options=options)
        self.driver.implicitly_wait(self.implicit_wait)
        logger.info("WebDriver initialized for testing")

    def _quit_driver(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def login(self, url: str, email: str, password: str, org_id: Optional[str] = None) -> bool:
        """Attempt to login with provided credentials."""
        try:
            logger.info(f"Attempting login to {url} with email: {email}")
            self.driver.get(url)
            time.sleep(3)

            # Try to find and fill email/username field
            email_selectors = [
                "input[name='email']",
                "input#email",
                "input[placeholder*='email' i]",
                "input[placeholder*='Email' i]",
                "input[name='username']",
                "input#username",
            ]

            email_element = None
            for selector in email_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        email_element = elements[0]
                        break
                except:
                    continue

            if not email_element:
                logger.warning("Email field not found, checking for login button")
                return False

            email_element.clear()
            email_element.send_keys(email)
            logger.info("Email entered")
            time.sleep(1)

            # Try to find and fill password field
            password_selectors = [
                "input[name='password']",
                "input#password",
                "input[placeholder*='password' i]",
                "input[placeholder*='Password' i]",
                "input[type='password']",
            ]

            password_element = None
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        password_element = elements[0]
                        break
                except:
                    continue

            if password_element:
                password_element.clear()
                password_element.send_keys(password)
                logger.info("Password entered")
                time.sleep(1)

            # Fill org_id if provided
            if org_id:
                org_id_selectors = [
                    "input[name='org_id']",
                    "input#org_id",
                    "input[placeholder*='org' i]",
                ]
                for selector in org_id_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements and elements[0].is_displayed():
                            elements[0].clear()
                            elements[0].send_keys(org_id)
                            logger.info("Org ID entered")
                            time.sleep(1)
                            break
                    except:
                        continue

            # Find and click submit button
            submit_selectors = [
                "button[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "button:contains('Submit')",
                "input[type='submit']",
                "//button[contains(text(), 'Login')]",
                "//button[contains(text(), 'Sign In')]",
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and elements[0].is_displayed():
                        submit_button = elements[0]
                        break
                except:
                    continue

            if submit_button:
                submit_button.click()
                logger.info("Submit button clicked")
                time.sleep(5)  # Wait for login to process

                # Check if login was successful
                if "login" not in self.driver.current_url.lower() and len(self.driver.current_url) > len(url):
                    logger.info(f"Login successful! Current URL: {self.driver.current_url}")
                    return True
                else:
                    logger.warning(f"Login may have failed. Current URL: {self.driver.current_url}")
                    return False
            else:
                logger.warning("Submit button not found")
                return False

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False

    def test_element_visibility(self, url: str, locator_by: str, locator_value: str) -> bool:
        """Test if an element is visible and clickable."""
        try:
            self.driver.get(url)
            time.sleep(2)

            by = By.CSS_SELECTOR if locator_by == "css selector" else By.XPATH
            element = WebDriverWait(self.driver, self.explicit_wait).until(
                EC.presence_of_element_located((by, locator_value))
            )
            return element.is_displayed()
        except Exception as e:
            logger.debug(f"Element visibility test failed: {e}")
            return False

    def test_element_clickability(self, url: str, locator_by: str, locator_value: str) -> bool:
        """Test if an element is clickable."""
        try:
            self.driver.get(url)
            time.sleep(2)

            by = By.CSS_SELECTOR if locator_by == "css selector" else By.XPATH
            element = WebDriverWait(self.driver, self.explicit_wait).until(
                EC.element_to_be_clickable((by, locator_value))
            )
            return True
        except Exception as e:
            logger.debug(f"Element clickability test failed: {e}")
            return False

    def run_comprehensive_test(self, url: str, email: str = None, password: str = None, org_id: str = None) -> Dict:
        """Run comprehensive tests on a website."""
        try:
            self._init_driver()
            
            results = {
                "url": url,
                "tests": {
                    "page_reachable": False,
                    "login_success": False,
                    "elements_found": 0,
                    "elements_visible": 0,
                    "elements_clickable": 0,
                },
                "errors": []
            }

            # Test 1: Page Reachability
            try:
                self.driver.get(url)
                time.sleep(2)
                if self.driver.current_url.startswith(url.split("?")[0]):
                    results["tests"]["page_reachable"] = True
                    logger.info(f"✓ Page reachable: {url}")
            except Exception as e:
                results["errors"].append(f"Page not reachable: {e}")
                logger.error(f"✗ Page not reachable: {e}")

            # Test 2: Login (if credentials provided)
            if email and password:
                login_success = self.login(url, email, password, org_id)
                results["tests"]["login_success"] = login_success
                if login_success:
                    logger.info("✓ Login successful")
                else:
                    logger.warning("✗ Login failed or skipped")

            # Test 3: Discover and test elements
            try:
                self.driver.get(url)
                time.sleep(2)

                elements = self.driver.find_elements(By.CSS_SELECTOR, "button, a, input[type='submit'], [role='button']")
                results["tests"]["elements_found"] = len(elements)
                logger.info(f"Found {len(elements)} interactive elements")

                visible_count = 0
                clickable_count = 0

                for elem in elements[:10]:  # Test first 10 elements
                    try:
                        if elem.is_displayed():
                            visible_count += 1
                        # Try to check if clickable
                        try:
                            elem.click()
                            clickable_count += 1
                            self.driver.back()
                            time.sleep(0.5)
                        except:
                            pass
                    except:
                        pass

                results["tests"]["elements_visible"] = visible_count
                results["tests"]["elements_clickable"] = clickable_count
                logger.info(f"✓ Visible elements: {visible_count}, Clickable: {clickable_count}")

            except Exception as e:
                results["errors"].append(f"Element discovery failed: {e}")
                logger.error(f"Element discovery failed: {e}")

            return results

        except Exception as e:
            logger.error(f"Comprehensive test failed: {e}")
            return {
                "url": url,
                "tests": {},
                "errors": [str(e)]
            }

        finally:
            self._quit_driver()


def run_autonomous_tests(url: str, email: str = None, password: str = None, org_id: str = None) -> Dict:
    """One-shot function to run autonomous tests."""
    executor = AutonomousTestExecutor(headless=True)
    return executor.run_comprehensive_test(url, email, password, org_id)


if __name__ == "__main__":
    # Example: Run autonomous tests
    url = "https://xelta.ai/"
    results = run_autonomous_tests(url, email="fake@gmail.com", password="Fake@123")
    print(results)
