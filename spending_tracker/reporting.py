# reporting.py
import os
from datetime import datetime

from .reporting_executive import generate_executive_summary
from .reporting_categories import generate_category_deep_dive
from .reporting_composition import generate_composition_report

def generate_all_reports(transactions, output_dir="reports"):
    """
    Main function to generate all spending reports.
    Creates a comprehensive analysis with multiple visualizations and insights.
    """
    print("\n" + "="*80)
    print("GENERATING COMPREHENSIVE SPENDING ANALYSIS")
    print("="*80 + "\n")

    os.makedirs(output_dir, exist_ok=True)

    if not transactions:
        print("No transactions found. Cannot generate reports.")
        return

    # Generate date for this report run
    report_date = datetime.now().strftime("%Y%m%d")
    report_subdir = os.path.join(output_dir, f"report_{report_date}")
    os.makedirs(report_subdir, exist_ok=True)

    print(f"📊 Reports will be saved to: {report_subdir}\n")

    # 1. Executive Summary
    print("\n" + "-"*80)
    print("1. EXECUTIVE SUMMARY")
    print("-"*80)
    generate_executive_summary(transactions, report_subdir)

    # 2. Category Deep Dive
    print("\n" + "-"*80)
    print("2. CATEGORY DEEP DIVE")
    print("-"*80)
    generate_category_deep_dive(transactions, report_subdir)

    # 3. Composition report
    print("\n" + "-"*80)
    print("2. COMPOSITION REPORT")
    print("-"*80)
    generate_composition_report(transactions, report_subdir)


    print("\n" + "="*80)
    print("✅ ALL REPORTS GENERATED SUCCESSFULLY")
    print(f"📁 Location: {report_subdir}")
    print("="*80 + "\n")

def view_uncategorized_transactions(transactions):
    """
    Displays a list of uncategorized transactions from a given list of transactions.
    """
    uncategorized_transactions = [t for t in transactions if t['category'] == "Uncategorized"]

    if not uncategorized_transactions:
        print("No uncategorized transactions found.")
        return

    print("\n--- Uncategorized Transactions (Sorted by Date) ---")
    for t in sorted(uncategorized_transactions, key=lambda x: x['date'], reverse=True):
        print(f"Date: {t['date']}, Amount: {t['amount']:>10.2f}, Bank: {t.get('bank', 'N/A'):<12}, Description: {t['description']}")

    print("\n--- Uncategorized Transactions (Sorted by Highest Absolute Value) ---")
    for t in sorted(uncategorized_transactions, key=lambda x: abs(x['amount']), reverse=True):
        print(f"Amount: {t['amount']:>10.2f}, Date: {t['date']}, Bank: {t.get('bank', 'N/A'):<12}, Description: {t['description']}")

    print("----------------------------------")
    print("\nTip: Edit config/categorization_map.yml to categorize these transactions.")