import pytest
import hashlib
import requests
from utils.data_reader import load_urls

@pytest.mark.regression
def test_homepage_hash_stable(base_url):
    # Basic "visual" regression via HTML hash. Store the value as a baseline per site.
    url = f"{base_url}/"
    r = requests.get(url, timeout=20)
    h = hashlib.sha256(r.text.encode("utf-8", errors="ignore")).hexdigest()
    # In a real project, load this from site-specific baseline storage.
    # We skip if no baseline is available yet.
    baseline = None
    if baseline is None:
        pytest.skip("No baseline hash set for homepage yet")
    assert h == baseline, f"Homepage HTML changed: {h} != {baseline}"
