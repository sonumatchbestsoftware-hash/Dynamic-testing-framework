#!/usr/bin/env python3
"""Debug script to check what elements are on xelta.ai homepage"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import sys

try:
    print("[*] Setting up Chrome driver...", file=sys.stderr)
    
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    print("[*] Navigating to https://xelta.ai/", file=sys.stderr)
    driver.get("https://xelta.ai/")
    
    print("[*] Waiting 5 seconds for JS to render...", file=sys.stderr)
    time.sleep(5)
    
    # Try XPath
    try:
        imgs_xpath = driver.find_elements(By.XPATH, "//img")
        print(f"\n[+] Found {len(imgs_xpath)} <img> elements", file=sys.stderr)
        for i, img in enumerate(imgs_xpath[:5]):
            print(f"    [{i}] alt={img.get_attribute('alt')[:40] if img.get_attribute('alt') else 'N/A'} " + 
                  f"src={img.get_attribute('src')[:60] if img.get_attribute('src') else 'N/A'}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Error finding images: {e}", file=sys.stderr)
    
    # Try the specific XPath we're using
    try:
        logo_xpath = "//img[contains(@src, 'logo') or contains(@alt, 'logo')]"
        logos = driver.find_elements(By.XPATH, logo_xpath)
        print(f"\n[+] Logo XPath query returned {len(logos)} results", file=sys.stderr)
        for logo in logos:
            print(f"    - {logo.get_attribute('alt') or 'no alt'}", file=sys.stderr)
    except Exception as e:
        print(f"[-] Error with logo XPath: {e}", file=sys.stderr)
    
    # Try simple XPath
    try:
        all_img = driver.find_elements(By.TAG_NAME, "img")
        print(f"\n[+] Found {len(all_img)} total images via TAG_NAME", file=sys.stderr)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
    
    # Get page title
    print(f"\n[+] Page Title: {driver.title}", file=sys.stderr)
    print(f"[+] Current URL: {driver.current_url}", file=sys.stderr)
    
    # Get page source snippet
    page_source = driver.page_source
    if 'img' in page_source:
        print(f"[+] Page has 'img' tags in source", file=sys.stderr)
    if 'logo' in page_source.lower():
        print(f"[+] Page has 'logo' text in source", file=sys.stderr)
    
    print(f"[+] Total page source length: {len(page_source)} bytes", file=sys.stderr)
    
    driver.quit()
    print("\n[*] Driver quit successfully", file=sys.stderr)
    
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
