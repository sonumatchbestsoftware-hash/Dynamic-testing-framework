import yaml
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_config():
    return load_yaml(ROOT / "config" / "test_config.yaml")

def load_locators():
    return load_yaml(ROOT / "config" / "locators.yaml")

def load_urls():
    xlsx = ROOT / "data" / "test_data.xlsx"
    return pd.read_excel(xlsx, sheet_name="urls")["url"].tolist()

def load_form(sheet='forms'):
    xlsx = ROOT / "data" / "test_data.xlsx"
    return pd.read_excel(xlsx, sheet_name=sheet).to_dict(orient="records")
