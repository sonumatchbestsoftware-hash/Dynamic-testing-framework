"""
Autonomous Locator Generator & Discovery Engine

Automatically discovers and generates accurate locators for UI elements
on any website using CSS selectors, XPath, ARIA roles, and data attributes.
"""

import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import yaml
from loguru import logger


class LocatorGenerator:
    """Discovers and generates accurate locators for UI elements."""

    def __init__(self, headless: bool = True, implicit_wait: int = 5, explicit_wait: int = 15):
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.explicit_wait = explicit_wait
        self.driver = None
        self.discovered_locators = {}
        self.element_strategies = []

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
        logger.info("WebDriver initialized")

    def _quit_driver(self):
        """Close WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def _generate_css_selector(self, element) -> Optional[str]:
        """Generate CSS selector for an element."""
        try:
            # Try to get element's data attributes first
            data_attrs = element.get_attribute("data-*")
            if data_attrs:
                elem_id = element.get_attribute("id")
                if elem_id:
                    return f"[id='{elem_id}']"
                name = element.get_attribute("name")
                if name:
                    return f"[name='{name}']"

            # Try ID
            elem_id = element.get_attribute("id")
            if elem_id:
                return f"#{elem_id}"

            # Try name
            name = element.get_attribute("name")
            if name:
                tag = element.tag_name
                return f"{tag}[name='{name}']"

            # Try class
            classes = element.get_attribute("class")
            if classes:
                class_list = classes.strip().split()
                if class_list:
                    return f"{element.tag_name}.{'.'.join(class_list[:3])}"

            # Try aria-label
            aria_label = element.get_attribute("aria-label")
            if aria_label:
                return f"[aria-label='{aria_label}']"

            # Try placeholder
            placeholder = element.get_attribute("placeholder")
            if placeholder:
                return f"[placeholder='{placeholder}']"

            # Try text content
            text = element.text.strip()
            if text:
                return f"{element.tag_name}:contains('{text[:30]}')"

            return None
        except Exception as e:
            logger.debug(f"Error generating CSS selector: {e}")
            return None

    def _generate_xpath(self, element) -> Optional[str]:
        """Generate XPath for an element."""
        try:
            # ID-based
            elem_id = element.get_attribute("id")
            if elem_id:
                return f"//*[@id='{elem_id}']"

            # Name-based
            name = element.get_attribute("name")
            if name:
                tag = element.tag_name
                return f"//{tag}[@name='{name}']"

            # Button/Link by text
            text = element.text.strip()
            if text and len(text) < 100:
                tag = element.tag_name
                return f"//{tag}[contains(text(), '{text[:50]}')]"

            # Class-based
            classes = element.get_attribute("class")
            if classes:
                class_list = classes.strip().split()
                if class_list:
                    class_str = " ".join(class_list[:2])
                    return f"//*[contains(@class, '{class_str}')]"

            # Data attributes
            data_testid = element.get_attribute("data-testid")
            if data_testid:
                return f"//*[@data-testid='{data_testid}']"

            data_test = element.get_attribute("data-test")
            if data_test:
                return f"//*[@data-test='{data_test}']"

            return None
        except Exception as e:
            logger.debug(f"Error generating XPath: {e}")
            return None

    def _get_element_info(self, element) -> Dict:
        """Extract comprehensive info about an element."""
        try:
            return {
                "tag": element.tag_name,
                "id": element.get_attribute("id"),
                "name": element.get_attribute("name"),
                "class": element.get_attribute("class"),
                "type": element.get_attribute("type"),
                "text": element.text.strip()[:100],
                "placeholder": element.get_attribute("placeholder"),
                "aria_label": element.get_attribute("aria-label"),
                "data_testid": element.get_attribute("data-testid"),
                "data_test": element.get_attribute("data-test"),
                "href": element.get_attribute("href"),
                "visible": element.is_displayed(),
            }
        except Exception as e:
            logger.debug(f"Error getting element info: {e}")
            return {}

    def discover_locators(self, url: str) -> Dict:
        """Discover all interactive elements and their locators on a page."""
        try:
            self._init_driver()
            self.driver.set_page_load_timeout(30)
            logger.info(f"Navigating to {url}")
            
            try:
                self.driver.get(url)
            except Exception as e:
                logger.warning(f"Page load timeout or error: {e}. Continuing with partial discovery.")
            
            time.sleep(3)  # Wait for page load

            # Define interactive elements to discover
            interactive_elements = [
                "button", "input", "a", "select", "textarea",
                "[role='button']", "[role='link']", "[role='menuitem']",
            ]

            locators = {}
            page_url = self.driver.current_url

            for selector in interactive_elements:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for idx, element in enumerate(elements):
                        try:
                            if not element.is_displayed():
                                continue

                            elem_key = f"{selector}_{idx}"
                            elem_info = self._get_element_info(element)
                            css_sel = self._generate_css_selector(element)
                            xpath_sel = self._generate_xpath(element)

                            locators[elem_key] = {
                                "by": "css selector" if css_sel else "xpath",
                                "value": css_sel or xpath_sel,
                                "type": elem_info.get("tag"),
                                "info": elem_info,
                            }
                        except Exception as e:
                            logger.debug(f"Error processing element: {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Error finding elements with selector {selector}: {e}")
                    continue

            self.discovered_locators[page_url] = locators
            logger.info(f"Discovered {len(locators)} locators on {page_url}")
            return locators

        except Exception as e:
            logger.error(f"Error discovering locators: {e}")
            return {}

        finally:
            try:
                self._quit_driver()
            except Exception as e:
                logger.debug(f"Error during driver cleanup: {e}")

    def save_locators_to_yaml(self, locators: Dict, output_path: str = "config/discovered_locators.yaml") -> Path:
        """Save discovered locators to a YAML file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Format for readability
            formatted = {}
            for page_url, page_locators in locators.items():
                page_key = page_url.split("://")[1].replace("/", "_").replace(".", "_")[:50]
                formatted[page_key] = {}
                for elem_key, loc in page_locators.items():
                    formatted[page_key][elem_key] = {
                        "by": loc["by"],
                        "value": loc["value"],
                        "type": loc["type"],
                    }

            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(formatted, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Locators saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving locators: {e}")
            raise

    def validate_locator(self, locator_by: str, locator_value: str, url: str) -> bool:
        """Validate that a locator works on a given URL."""
        try:
            self._init_driver()
            self.driver.get(url)
            time.sleep(2)

            by = By.CSS_SELECTOR if locator_by == "css selector" else By.XPATH
            element = WebDriverWait(self.driver, self.explicit_wait).until(
                EC.presence_of_element_located((by, locator_value))
            )
            return element.is_displayed()
        except Exception as e:
            logger.debug(f"Locator validation failed: {e}")
            return False
        finally:
            self._quit_driver()


def auto_discover_and_save(url: str, output_path: str = "config/discovered_locators.yaml") -> Path:
    """One-shot function to discover and save locators."""
    generator = LocatorGenerator(headless=True)
    locators = generator.discover_locators(url)
    return generator.save_locators_to_yaml(locators, output_path)


if __name__ == "__main__":
    # Example: Discover locators on a website
    url = "https://xelta.ai/"
    output = auto_discover_and_save(url)
    print(f"Locators saved to: {output}")
