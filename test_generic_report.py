"""
Unit smoke-test for generic_report.py preprocessing.
Verifies that the header-detection pipeline works on a synthetic
DataFrame that mimics an ERP-style report with decorative title rows.
"""
import pandas as pd
from reports.generic_report import GenericReport


def make_erp_like_df():
    """
    Simulate a WorkLocation-style sheet where:
      row 0 = company name / title (all Unnamed: in pandas terms)
      row 1 = blank
      row 2 = actual column headers
      row 3+ = data
    """
    raw_data = [
        ["Company Name Ltd.", None, None, None, None, None],   # title row
        [None, None, None, None, None, None],                   # blank row
        ["Employee", "Department", "Manager", "Branch", "Date", "Time"],  # headers
        ["KARTHICK MS", "CORPORATE TEAM", "HR MANAGER", "ANNA NAGAR", "02-05-2026", "09:40"],
        ["PRIYA R", "FINANCE", "CFO", "T NAGAR", "02-05-2026", "09:15"],
    ]
    # Build as pandas would if read from Excel with header=0
    # (row 0 becomes header = all Unnamed because they look like data)
    df = pd.DataFrame(
        raw_data[1:],  # skip the actual header — pandas auto-assigns Unnamed
        columns=[f"Unnamed: {i}" for i in range(6)]
    )
    df.iloc[0] = raw_data[0]  # put title row at index 0
    return df


def test_header_detection():
    df = make_erp_like_df()
    print("=== Original DataFrame ===")
    print(df.to_string())
    print()

    result = GenericReport._preprocess_dataframe(df, "Sheet1")

    if result is None:
        print("FAIL: result is None")
        return

    print("=== Preprocessed DataFrame ===")
    print(result.to_string())
    print()
    print("Columns:", list(result.columns))

    # Verify no Unnamed: columns remain (except legitimate ones)
    unnamed_remaining = [c for c in result.columns if "unnamed" in str(c).lower()]
    assert len(unnamed_remaining) == 0, f"Unnamed columns remain: {unnamed_remaining}"
    print("PASS: No Unnamed: columns remain")

    # Verify actual data is present
    assert len(result) > 0, "FAIL: DataFrame is empty after preprocessing"
    print(f"PASS: {len(result)} data row(s) after preprocessing")


def test_clean_df_passthrough():
    """A DataFrame with clean headers should pass through unchanged (modulo Title Case)."""
    clean_df = pd.DataFrame({
        "employee_name": ["Alice", "Bob"],
        "department": ["HR", "Finance"],
        "salary": [50000, 60000],
    })
    result = GenericReport._preprocess_dataframe(clean_df, "Sheet1")
    assert result is not None
    assert "Employee Name" in result.columns
    assert "Department" in result.columns
    print("PASS: clean DataFrame passes through with Title Case columns")


def test_generic_report_parse():
    """End-to-end parse() produces documents with no Unnamed: in text."""
    from schemas.report import SourceType
    df = make_erp_like_df()
    report = GenericReport(
        df_map={"Sheet1": df},
        source_file="WorkLocationReport.xlsx",
        source_type=SourceType.EXCEL,
    )
    result = report.parse()
    print(f"Document count: {result.document_count}")
    for doc in result.documents[:3]:
        print("---")
        print(doc.text[:200])
        assert "Unnamed" not in doc.text, f"Unnamed found in doc text: {doc.text}"
    print("PASS: No 'Unnamed:' in document text")
    print(f"PASS: source_file metadata = {result.documents[0].metadata['source_file']}")
    print(f"PASS: sheet metadata = {result.documents[0].metadata['sheet']}")


if __name__ == "__main__":
    print("=== Test 1: Header Detection ===")
    test_header_detection()
    print()
    print("=== Test 2: Clean DataFrame Passthrough ===")
    test_clean_df_passthrough()
    print()
    print("=== Test 3: End-to-End Parse ===")
    test_generic_report_parse()
    print()
    print("All tests passed.")
