#!/usr/bin/env python3
"""Inspect xelta.ai page and find actual element selectors."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def inspect_page(url):
    """Inspect a page and find all relevant elements."""
    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        print(f"\n{'='*60}")
        print(f"Inspecting: {url}")
        print(f"{'='*60}\n")
        
        driver.get(url)
        time.sleep(3)
        
        # Look for images (logos)
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"Found {len(images)} images:")
        for i, img in enumerate(images[:10]):  # First 10
            alt = img.get_attribute("alt") or ""
            src = img.get_attribute("src") or ""[:80]
            cls = img.get_attribute("class") or ""
            id_ = img.get_attribute("id") or ""
            print(f"  [{i}] <img alt='{alt}' class='{cls}' id='{id_}' src='{src}...'/>")
        
        # Look for buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\nFound {len(buttons)} buttons:")
        for i, btn in enumerate(buttons[:10]):
            text = btn.text[:50]
            cls = btn.get_attribute("class") or ""
            id_ = btn.get_attribute("id") or ""
            data_test = btn.get_attribute("data-testid") or ""
            print(f"  [{i}] <button text='{text}' class='{cls}' id='{id_}' data-testid='{data_test}'/>")
        
        # Look for form inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\nFound {len(inputs)} input fields:")
        for i, inp in enumerate(inputs[:10]):
            type_ = inp.get_attribute("type") or ""
            name = inp.get_attribute("name") or ""
            placeholder = inp.get_attribute("placeholder") or ""
            cls = inp.get_attribute("class") or ""
            print(f"  [{i}] <input type='{type_}' name='{name}' placeholder='{placeholder}' class='{cls}'/>")
        
        # Look for links
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"\nFound {len(links)} links:")
        for i, link in enumerate(links[:15]):
            text = link.text[:50]
            href = link.get_attribute("href") or ""[:80]
            cls = link.get_attribute("class") or ""
            print(f"  [{i}] <a text='{text}' href='{href}...' class='{cls}'/>")
        
        # Look for main container elements
        print(f"\nPage Title: {driver.title}")
        print(f"Page URL: {driver.current_url}")
        
        # Get all elements with class names containing "logo", "cta", "hero", etc.
        special_elements = driver.execute_script("""
            return {
                logo_elements: document.querySelectorAll('[class*="logo"], [id*="logo"]').length,
                cta_elements: document.querySelectorAll('[class*="cta"], [class*="button"], [class*="btn"]').length,
                header_elements: document.querySelectorAll('header, [role="banner"]').length,
                form_elements: document.querySelectorAll('form, [role="form"]').length,
                nav_elements: document.querySelectorAll('nav, [role="navigation"]').length,
            };
        """)
        print(f"\nSpecial element counts: {json.dumps(special_elements, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    # Inspect both pages
    inspect_page("https://xelta.ai/")
    inspect_page("https://xelta.ai/auth/login/")
