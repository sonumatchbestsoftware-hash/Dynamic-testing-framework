"""
Autonomous Test Runner - Orchestrates locator discovery and comprehensive testing
"""

import sys
from pathlib import Path
from utils.locator_generator import auto_discover_and_save, LocatorGenerator
from utils.autonomous_tester import run_autonomous_tests
from utils.data_reader import load_config
from loguru import logger
import subprocess

# Configure logging
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add(Path("reports") / "autonomous_tests.log", level="DEBUG")


def main():
    """Run the full autonomous testing pipeline."""
    
    print("\n" + "="*80)
    print("AUTONOMOUS DYNAMIC TEST AUTOMATION FRAMEWORK")
    print("="*80 + "\n")

    # Load configuration
    try:
        config = load_config()
        base_url = config.get("base_url", "").rstrip("/")
        email = config.get("credentials", {}).get("username", "")
        password = config.get("credentials", {}).get("password", "")
        org_id = config.get("credentials", {}).get("org_id", "")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    print(f"📍 Target URL: {base_url}")
    print(f"👤 Email: {email}")
    print(f"🔐 Password: {'*' * len(password)}")
    print()

    # Step 1: Discover locators
    print("Step 1: Discovering UI Elements & Locators...")
    print("-" * 80)
    try:
        locators_path = auto_discover_and_save(base_url, "config/discovered_locators.yaml")
        print(f"✓ Locators discovered and saved to: {locators_path}\n")
    except Exception as e:
        logger.error(f"Failed to discover locators: {e}")
        print(f"⚠️  Locator discovery failed (may be network issue): {e}")
        print(f"    Continuing with existing locators...\n")

    # Step 2: Run autonomous tests
    print("Step 2: Running Autonomous Tests...")
    print("-" * 80)
    try:
        test_results = run_autonomous_tests(base_url, email, password, org_id)
        
        print(f"\n📊 Test Results for {test_results['url']}:")
        print(f"  ✓ Page Reachable: {test_results['tests'].get('page_reachable', False)}")
        print(f"  ✓ Login Success: {test_results['tests'].get('login_success', False)}")
        print(f"  ✓ Elements Found: {test_results['tests'].get('elements_found', 0)}")
        print(f"  ✓ Elements Visible: {test_results['tests'].get('elements_visible', 0)}")
        print(f"  ✓ Elements Clickable: {test_results['tests'].get('elements_clickable', 0)}")
        
        if test_results.get('errors'):
            print(f"\n  ⚠️  Errors:")
            for error in test_results['errors']:
                print(f"     - {error}")
        print()
    except Exception as e:
        logger.error(f"Failed to run autonomous tests: {e}")
        print(f"✗ Autonomous tests failed: {e}\n")

    # Step 3: Run full pytest suite
    print("Step 3: Running Full Pytest Suite...")
    print("-" * 80)
    try:
        result = subprocess.run(
            ["./.venv/Scripts/python.exe", "run_tests.py"],
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            print("\n✓ All tests passed!\n")
        else:
            print(f"\n⚠️  Some tests failed or skipped (exit code: {result.returncode})\n")
    except Exception as e:
        logger.error(f"Failed to run pytest: {e}")
        print(f"✗ Pytest execution failed: {e}\n")

    print("="*80)
    print("AUTONOMOUS TESTING COMPLETE")
    print("="*80)
    print("\nCheck the following for detailed results:")
    print("  - reports/latest_report.html (HTML report)")
    print("  - reports/summary.xlsx (Excel summary)")
    print("  - reports/junit.xml (JUnit format)")
    print("  - reports/autonomous_tests.log (Detailed log)")


if __name__ == "__main__":
    main()
