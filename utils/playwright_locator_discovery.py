#!/usr/bin/env python3
"""Discover likely locators on a page using Playwright (headless Chromium).

Outputs YAML fragment to stdout that can be pasted into `config/locators.yaml`.
"""
import sys
import yaml
from playwright.sync_api import sync_playwright


def discover(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)

        # Wait a bit for client-side rendering
        page.wait_for_timeout(1500)

        data = {
            'homepage': {},
            'auth': {}
        }

        # Logo candidates: img with src containing 'logo' or alt containing 'logo', svg with role img
        logos = page.query_selector_all("img[src*=logo], img[alt*=logo], svg[class*=logo]")
        if logos:
            sel = []
            for el in logos[:3]:
                try:
                    src = el.get_attribute('src') or ''
                    alt = el.get_attribute('alt') or ''
                    if src:
                        sel.append(f"//img[contains(@src, '{src.split('/')[-1]}')]")
                    elif alt:
                        sel.append(f"//img[contains(@alt, '{alt}')]")
                except Exception:
                    continue
            data['homepage']['logo'] = {'by': 'xpath', 'value': ' | '.join(sel)}

        # CTA candidates: visible buttons or links with keywords
        cta_selectors = []
        candidates = page.query_selector_all("button, a")
        for el in candidates:
            try:
                text = (el.inner_text() or '').strip()
                if not text:
                    continue
                low = text.lower()
                if any(k in low for k in ('start', 'get started', 'sign up', 'try', 'launch', 'create')):
                    # build XPath using text
                    cta_selectors.append(f"//button[contains(normalize-space(.), '{text}')]|//a[contains(normalize-space(.), '{text}')]")
                if len(cta_selectors) >= 3:
                    break
            except Exception:
                continue
        if cta_selectors:
            data['homepage']['primary_cta'] = {'by': 'xpath', 'value': ' | '.join(cta_selectors)}

        # Inputs for auth: email/username and password
        # try common attributes
        try:
            email_el = page.query_selector("input[type='email'], input[name*=email], input[placeholder*=email]")
            if email_el:
                # build XPath by name or type
                name = email_el.get_attribute('name')
                ph = email_el.get_attribute('placeholder')
                if name:
                    data['auth']['username'] = {'by': 'xpath', 'value': f"//input[@name='{name}']"}
                elif ph:
                    data['auth']['username'] = {'by': 'xpath', 'value': f"//input[contains(@placeholder, '{ph}')]"}
                else:
                    data['auth']['username'] = {'by': 'xpath', 'value': "//input[@type='email']"}
        except Exception:
            pass

        try:
            pwd_el = page.query_selector("input[type='password']")
            if pwd_el:
                name = pwd_el.get_attribute('name')
                if name:
                    data['auth']['password'] = {'by': 'xpath', 'value': f"//input[@name='{name}']"}
                else:
                    data['auth']['password'] = {'by': 'xpath', 'value': "//input[@type='password']"}
        except Exception:
            pass

        # submit button in form
        try:
            # find button[type=submit] in the page
            submit = page.query_selector("button[type='submit'], input[type='submit'], button:has-text('Log in'), button:has-text('Login'), button:has-text('Sign in')")
            if submit:
                text = (submit.inner_text() or '').strip()
                if text:
                    sel = f"//button[contains(normalize-space(.), '{text}')] | //input[@type='submit']"
                else:
                    sel = "//button[@type='submit'] | //input[@type='submit']"
                data['auth']['submit'] = {'by': 'xpath', 'value': sel}
        except Exception:
            pass

        browser.close()
        return data


if __name__ == '__main__':
    url = 'https://xelta.ai/auth/login/'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    res = discover(url)
    print(yaml.safe_dump(res, sort_keys=False))
