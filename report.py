# spending_tracker/reporting_main.py
from spending_tracker import reporting
from spending_tracker.loader import load_and_categorize_transactions

if __name__ == "__main__":
    """Generates all spending reports."""
    print("Generating reports")
    transactions = load_and_categorize_transactions()
    reporting.generate_all_reports(transactions)
