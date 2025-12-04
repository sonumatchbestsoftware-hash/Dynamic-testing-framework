#!/usr/bin/env python3
"""Quick inspection of xelta.ai using a simple Selenium approach."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import sys

try:
    print("Starting browser inspection of xelta.ai...", file=sys.stderr)
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    print("\n=== XELTA.AI HOMEPAGE ===\n", file=sys.stderr)
    driver.get("https://xelta.ai/")
    
    # Simple JavaScript to extract useful information
    result = driver.execute_script("""
        return {
            title: document.title,
            url: window.location.href,
            images: Array.from(document.querySelectorAll('img')).map(img => ({
                src: img.src.substring(0, 100),
                alt: img.alt,
                class: img.className,
                id: img.id
            })).slice(0, 5),
            buttons: Array.from(document.querySelectorAll('button, [role="button"]')).map(btn => ({
                text: btn.textContent.substring(0, 50),
                class: btn.className,
                id: btn.id
            })).slice(0, 5),
            links: Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.textContent.substring(0, 50),
                href: a.href.substring(0, 100),
                class: a.className
            })).slice(0, 10)
        };
    """)
    
    import json
    print(json.dumps(result, indent=2))
    
    driver.quit()
    
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
