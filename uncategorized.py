# spending_tracker/uncategorized_main.py
from datetime import datetime
from dateutil.relativedelta import relativedelta
from spending_tracker import reporting
from spending_tracker.loader import load_and_categorize_transactions

if __name__ == "__main__":
    """Views uncategorized transactions from the last two years."""
    transactions = load_and_categorize_transactions()

    # Filter for last two years
    two_years_ago = datetime.now().date() - relativedelta(years=2)
    recent_transactions = [t for t in transactions if t['date'] >= two_years_ago]

    reporting.view_uncategorized_transactions(recent_transactions)
