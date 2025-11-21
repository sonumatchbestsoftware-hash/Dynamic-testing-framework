from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd

def junit_to_excel(junit_xml_path: Path, out_xlsx_path: Path):
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
            if case.find("failure") is not None:
                status = "failed"
                message = case.find("failure").attrib.get("message", "")
            elif case.find("error") is not None:
                status = "error"
                message = case.find("error").attrib.get("message", "")
            elif case.find("skipped") is not None:
                status = "skipped"
                message = case.find("skipped").attrib.get("message", "")

            rows.append({
                "suite": suite_name,
                "test": name,
                "classname": classname,
                "time": time,
                "status": status,
                "message": message
            })

    df = pd.DataFrame(rows)
    with pd.ExcelWriter(out_xlsx_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="results", index=False)

if __name__ == "__main__":
    # Example usage for manual runs
    junit_to_excel("reports/junit.xml", "reports/summary.xlsx")
