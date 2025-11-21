import subprocess
from pathlib import Path
from utils.report_writer import junit_to_excel

REPORTS = Path("reports")
HTML = REPORTS / "latest_report.html"
JUNIT = REPORTS / "junit.xml"
XLSX = REPORTS / "summary.xlsx"

def main():
    REPORTS.mkdir(exist_ok=True, parents=True)
    # Run pytest with HTML + JUnit outputs
    subprocess.run(
        f"pytest -q --html={HTML} --self-contained-html --junitxml={JUNIT}",
        shell=True,
        check=False  # avoid raising if tests skip/fail
    )
    # Convert JUnit -> Excel summary
    if JUNIT.exists():
        junit_to_excel(JUNIT, XLSX)
        print(f"\nExcel summary written to: {XLSX}\n")
    else:
        print("\nJUnit XML not found; Excel summary not generated.\n")

if __name__ == "__main__":
    main()
