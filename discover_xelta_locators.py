"""Quick locator discovery script for xelta.ai"""
from utils.locator_generator import LocatorGenerator
import yaml

gen = LocatorGenerator(headless=True)
print('🔍 Discovering locators from xelta.ai homepage...\n')

locators = gen.discover_locators('https://xelta.ai/')
print(f'✓ Found {len(locators)} interactive elements\n')

# Group by element type
by_type = {}
for key, loc in locators.items():
    elem_type = loc['type']
    if elem_type not in by_type:
        by_type[elem_type] = []
    by_type[elem_type].append({
        'key': key,
        'by': loc['by'],
        'value': loc['value'],
        'info': loc['info']
    })

# Print summary
for elem_type, items in sorted(by_type.items()):
    print(f"Found {len(items)} {elem_type} elements:")
    for item in items[:3]:  # Show first 3 of each type
        info = item['info']
        text = info.get('text', '')[:40] if info.get('text') else ''
        aria = info.get('aria_label', '')[:40] if info.get('aria_label') else ''
        label = text or aria or item['value'][:40]
        print(f"  • {item['by']}: {label}")
    if len(items) > 3:
        print(f"  ... and {len(items) - 3} more\n")

# Save to file
output_path = gen.save_locators_to_yaml(gen.discovered_locators, "config/discovered_locators.yaml")
print(f"\n✓ Locators saved to {output_path}")
