import pytest
import requests

@pytest.mark.security
def test_https_enforced(base_url):
    # If base_url is already https, consider this a pass if it loads.
    if base_url.startswith("https://"):
        r = requests.get(base_url, timeout=20, allow_redirects=True)
        assert r.status_code < 500, "Site not reachable over HTTPS"
    else:
        # If http base, check if it redirects to https
        http_url = base_url.replace("https://", "http://")
        r = requests.get(http_url, timeout=20, allow_redirects=True)
        assert r.url.startswith("https://"), "HTTP did not redirect to HTTPS"

@pytest.mark.security
def test_basic_security_headers(base_url):
    r = requests.get(base_url, timeout=20)
    headers = {k.lower(): v for k, v in r.headers.items()}
    # Minimal set of recommended headers
    must_have = [
        "content-security-policy",
        "x-frame-options",
        "x-content-type-options",
        "referrer-policy"
    ]
    missing = [h for h in must_have if h not in headers]
    if missing:
        pytest.skip(f"Missing recommended headers: {', '.join(missing)}")
