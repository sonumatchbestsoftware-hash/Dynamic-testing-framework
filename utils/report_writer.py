from pathlib import Path
import xml.etree.ElementTree as ET
import sys

try:
    import pandas as pd
    _HAS_PANDAS = True
except Exception:
    pd = None
    _HAS_PANDAS = False


def _get_message_from_element(elem):
    if elem is None:
        return ""
    # Prefer 'message' attribute, fall back to text content
    msg = elem.attrib.get("message") if elem.attrib else None
    if msg:
        return msg
    return (elem.text or "").strip()


def junit_to_excel(junit_xml_path: Path, out_xlsx_path: Path):
    """Convert a pytest JUnit XML report into an Excel (.xlsx) file.

    If pandas/openpyxl are not available, falls back to writing a CSV file
    with the same base name.
    """
    junit_xml_path = Path(junit_xml_path)
    out_xlsx_path = Path(out_xlsx_path)
    out_xlsx_path.parent.mkdir(parents=True, exist_ok=True)

    if not junit_xml_path.exists():
        raise FileNotFoundError(f"JUnit XML not found: {junit_xml_path}")

    tree = ET.parse(junit_xml_path)
    root = tree.getroot()

    rows = []
    # Works for both <testsuite> root or <testsuites>
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    for suite in suites:
        suite_name = suite.attrib.get("name", "suite")
        for case in suite.findall("testcase"):
            name = case.attrib.get("name")
            classname = case.attrib.get("classname")
            time = case.attrib.get("time")
            status = "passed"
            message = ""
            failure = case.find("failure")
            error = case.find("error")
            skipped = case.find("skipped")
            if failure is not None:
                status = "failed"
                message = _get_message_from_element(failure)
            elif error is not None:
                status = "error"
                message = _get_message_from_element(error)
            elif skipped is not None:
                status = "skipped"
                message = _get_message_from_element(skipped)

            rows.append({
                "suite": suite_name,
                "test": name,
                "classname": classname,
                "time": time,
                "status": status,
                "message": message
            })

    # If pandas is available, write an .xlsx using openpyxl engine.
    if _HAS_PANDAS:
        try:
            df = pd.DataFrame(rows)
            with pd.ExcelWriter(out_xlsx_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="results", index=False)
            return out_xlsx_path
        except Exception:
            # Fall through to CSV fallback on any error
            pass

    # Fallback: write CSV with same base name
    csv_path = out_xlsx_path.with_suffix(".csv")
    try:
        # Lightweight CSV write without pandas
        import csv

        with open(csv_path, "w", newline="", encoding="utf-8") as fh:
            if not rows:
                return csv_path
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            for r in rows:
                writer.writerow({k: (v if v is not None else "") for k, v in r.items()})
        return csv_path
    except Exception:
        raise


if __name__ == "__main__":
    # Example usage for manual runs
    try:
        junit_to_excel("reports/junit.xml", "reports/summary.xlsx")
    except Exception as e:
        print("Error converting JUnit to Excel:", e, file=sys.stderr)
