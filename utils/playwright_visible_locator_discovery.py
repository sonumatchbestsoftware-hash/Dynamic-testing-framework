#!/usr/bin/env python3
"""Discover visible locators using Playwright and prefer visible elements.

Prints a YAML fragment with best visible selectors for `homepage` and `auth`.
"""
import sys
import yaml
from playwright.sync_api import sync_playwright


def discover_visible(url, timeout=30000):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=timeout)
        page.wait_for_timeout(1000)

        data = {'homepage': {}, 'auth': {}}

        # Check logo candidates
        logo_css_candidates = [
            "img[src*='logo']",
            "img[alt*='logo']",
            "svg[class*='logo']",
            "[class*='logo'] img",
            "header img",
        ]
        logo_sel = None
        for sel in logo_css_candidates:
            try:
                if page.query_selector(sel) and page.is_visible(sel):
                    logo_sel = sel
                    break
            except Exception:
                continue
        if logo_sel:
            data['homepage']['logo'] = {'by': 'css selector', 'value': logo_sel}

        # CTA: look for visible buttons/links with CTA-like text
        cta_text_keys = ['sign up', 'get started', 'start free', 'try now', 'get access']
        cta_sel = None
        # prefer buttons
        for btn in page.query_selector_all('button, a'):
            try:
                txt = (btn.inner_text() or '').strip()
                if not txt:
                    continue
                low = txt.lower()
                if any(k in low for k in cta_text_keys):
                    # get a robust CSS selector via data-testid or class fallback
                    data_test = btn.get_attribute('data-testid')
                    cls = btn.get_attribute('class')
                    if data_test:
                        sel = f"[data-testid='{data_test}']"
                    elif cls:
                        # take first class
                        first_cls = cls.split()[0]
                        sel = f".{first_cls}"
                    else:
                        # use text selector via XPath
                        sel = f"xpath=//button[contains(normalize-space(.), '{txt}')] | xpath=//a[contains(normalize-space(.), '{txt}')]"
                    # check visibility
                    try:
                        if sel.startswith('xpath='):
                            # page.is_visible works with xpath= prefix
                            if page.is_visible(sel):
                                cta_sel = sel
                                break
                        else:
                            if page.is_visible(sel):
                                cta_sel = sel
                                break
                    except Exception:
                        # final fallback: try visibility of the element itself
                        if btn.is_visible():
                            # prefer text-based xpath
                            sel = f"xpath=//button[contains(normalize-space(.), '{txt}')] | xpath=//a[contains(normalize-space(.), '{txt}')]"
                            cta_sel = sel
                            break
            except Exception:
                continue
        if cta_sel:
            # normalize output: strip xpath= prefix for YAML to use 'xpath' type
            if cta_sel.startswith('xpath='):
                sel_value = cta_sel.replace('xpath=', '')
                data['homepage']['primary_cta'] = {'by': 'xpath', 'value': sel_value}
            else:
                data['homepage']['primary_cta'] = {'by': 'css selector', 'value': cta_sel}

        # Auth page detection: look for visible email and password inputs
        email_sel = None
        pwd_sel = None
        for s in ["input[type='email']", "input[name*=email]", "input[placeholder*='email']"]:
            try:
                if page.query_selector(s) and page.is_visible(s):
                    email_sel = s
                    break
            except Exception:
                continue
        for s in ["input[type='password']", "input[name*=pass]", "input[placeholder*='password']"]:
            try:
                if page.query_selector(s) and page.is_visible(s):
                    pwd_sel = s
                    break
            except Exception:
                continue
        if email_sel:
            data['auth']['username'] = {'by': 'css selector', 'value': email_sel}
        if pwd_sel:
            data['auth']['password'] = {'by': 'css selector', 'value': pwd_sel}

        # submit button visible
        submit_sel = None
        for s in ["button[type='submit']", "input[type='submit']", "button:has-text('Log in')", "button:has-text('Login')", "button:has-text('Sign in')"]:
            try:
                if page.query_selector(s) and page.is_visible(s):
                    submit_sel = s
                    break
            except Exception:
                continue
        if submit_sel:
            data['auth']['submit'] = {'by': 'css selector', 'value': submit_sel}

        browser.close()
        return data


if __name__ == '__main__':
    url = 'https://xelta.ai/'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    try:
        out = discover_visible(url)
        print(yaml.safe_dump(out, sort_keys=False))
    except Exception as e:
        print('error:', e)
        sys.exit(1)
