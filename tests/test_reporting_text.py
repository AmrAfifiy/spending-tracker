import datetime
from spending_tracker.reporting_text import generate_textual_report

def test_generate_textual_report(tmp_path):
    transactions = [
        {"date": datetime.date(2026, 8, 1), "amount": -100.0, "category": "Groceries", "description": "Tesco"},
        {"date": datetime.date(2026, 7, 10), "amount": -50.0, "category": "Eating Out", "description": "Hawksmoor"},
        {"date": datetime.date(2026, 7, 15), "amount": -120.0, "category": "Groceries", "description": "Sainsburys"},
    ]
    
    out_dir = tmp_path / "test_report"
    out_dir.mkdir()
    
    # Executing on Aug 8 (< 15th) -> reporting month should be July 2026 (2026-07)
    generate_textual_report(transactions, str(out_dir), base_date=datetime.date(2026, 8, 8))
    
    json_file = out_dir / "llm_report_data.json"
    md_file = out_dir / "llm_report_summary.md"
    
    assert json_file.exists()
    assert md_file.exists()
    
    md_content = md_file.read_text()
    assert "Financial Spending Summary (July 2026)" in md_content
    assert "2026-07" in md_content
    assert "2026-08" not in md_content

