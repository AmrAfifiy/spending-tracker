# reporting_categories.py (Updated)
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

def get_top_categories_by_average(transactions, top_n=8, months_back=12, base_date=None):
    """Get categories with highest average spending over time period."""
    if base_date is None:
        base_date = datetime.now().date()
    
    category_totals = defaultdict(float)

    start_date = base_date.replace(day=1) - relativedelta(months=months_back-1)
    end_date = base_date.replace(day=1) + relativedelta(months=1)

    for t in transactions:
        if start_date <= t['date'] < end_date and t['amount'] < 0:
            category_totals[t['category']] += abs(t['amount'])

    # Calculate averages
    category_averages = {cat: total / months_back for cat, total in category_totals.items()}

    # Sort by average and get top N
    sorted_cats = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
    return [(cat, avg) for cat, avg in sorted_cats[:top_n]]

def get_category_history(transactions, category, months_back=12, base_date=None):
    """Get monthly spending history for a specific category."""
    if base_date is None:
        base_date = datetime.now().date()
        
    history = {}

    for i in range(months_back - 1, -1, -1):
        month_start = (base_date.replace(day=1) - relativedelta(months=i))
        month_end = month_start + relativedelta(months=1)
        month_str = month_start.strftime('%Y-%m')

        total = sum(abs(t['amount']) for t in transactions
                   if month_start <= t['date'] < month_end
                   and t['amount'] < 0
                   and t['category'] == category)

        history[month_str] = total

    return history

def detect_recurring_transactions(transactions, category):
    """Detect potential recurring transactions/subscriptions in a category."""
    category_transactions = [t for t in transactions if t['category'] == category and t['amount'] < 0]

    # Group by similar amounts (within £1)
    amount_groups = defaultdict(list)
    for t in category_transactions:
        amount_key = round(abs(t['amount']))
        amount_groups[amount_key].append(t)

    recurring = []
    for amount_key, trans in amount_groups.items():
        if len(trans) >= 3:  # At least 3 occurrences
            # Check if they're roughly monthly
            dates = sorted([t['date'] for t in trans])
            if len(dates) >= 3:
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_interval = sum(intervals) / len(intervals)

                # If average interval is between 25-35 days, likely monthly
                if 25 <= avg_interval <= 35:
                    avg_amount = sum(abs(t['amount']) for t in trans) / len(trans)
                    descriptions = list(set(t['description'] for t in trans))
                    recurring.append({
                        'amount': avg_amount,
                        'frequency': 'Monthly',
                        'count': len(trans),
                        'descriptions': descriptions[:3]  # Show up to 3 unique descriptions
                    })

    return recurring

def generate_category_deep_dive(transactions, output_dir):
    """Generate detailed category analysis for top spending categories."""

    today = datetime.now().date()

    # Determine the reporting month based on the day of the month
    if today.day < 15:
        # If before the 15th, report on the previous month
        report_month_start = (today.replace(day=1) - relativedelta(days=1)).replace(day=1)
    else:
        # Otherwise, report on the current month
        report_month_start = today.replace(day=1)

    report_month_end = report_month_start + relativedelta(months=1)

    # Get top categories by 12-month average (up to the reporting month)
    top_categories_with_avg = [
        (cat, avg) for cat, avg in get_top_categories_by_average(transactions, top_n=10, months_back=12, base_date=report_month_start)
        if cat not in ['Car', 'Medical & Dental']
    ]

    if not top_categories_with_avg:
        print("No spending data available.")
        return

    # Get reporting month spending for these categories
    current_spending = {}
    for t in transactions:
        if report_month_start <= t['date'] < report_month_end and t['amount'] < 0:
            cat = t['category']
            if any(cat == top_cat for top_cat, _ in top_categories_with_avg):
                if cat not in current_spending:
                    current_spending[cat] = 0
                current_spending[cat] += abs(t['amount'])

    # Create sorted list maintaining top categories order
    sorted_categories = [(cat, current_spending.get(cat, 0)) for cat, _ in top_categories_with_avg]

    print(f"\n📅 Reporting Month: {report_month_start.strftime('%B %Y')}")
    print(f"📊 Analyzing Top 5 Categories (by 12-mo average)...\n")

    # Analyze top 5 categories
    for i, (category, current_amount) in enumerate(sorted_categories[:5], 1):
        # Get 12-month average for this category
        avg_for_cat = next((avg for cat, avg in top_categories_with_avg if cat == category), 0)
        variance_from_avg = ((current_amount - avg_for_cat) / avg_for_cat * 100) if avg_for_cat > 0 else 0

        # Build a single line summary
        trend_icon = "➡️"
        history = get_category_history(transactions, category, months_back=12, base_date=report_month_start)
        amounts_list = [v for v in history.values() if v > 0]
        if len(amounts_list) >= 3:
            recent_avg = sum(amounts_list[-3:]) / 3
            earlier_avg = sum(amounts_list[-6:-3]) / 3 if len(amounts_list) >= 6 else (sum(amounts_list[:-3]) / len(amounts_list[:-3]) if len(amounts_list) > 3 else 0)
            if recent_avg > earlier_avg * 1.1: trend_icon = "📈"
            elif recent_avg < earlier_avg * 0.9: trend_icon = "📉"

        print(f" {trend_icon} {category:<18}: £{current_amount:>8,.2f} (Avg: £{avg_for_cat:>8,.2f}, Var: {variance_from_avg:>+5.1f}%)")

        # Check for recurring transactions only if significant
        recurring = detect_recurring_transactions(transactions, category)
        if recurring:
            for rec in recurring:
                if rec['amount'] > 20: # Only show significant recurring
                    print(f"      🔄 Recurring: £{rec['amount']:.2f} ({', '.join(rec['descriptions'][:1])})")

    # Generate visualizations for top categories
    fig = plt.figure(figsize=(16, 12))

    # Create subplots for top categories
    for idx in range(min(len(sorted_categories), 9)):
        category, _ = sorted_categories[idx]

        ax = plt.subplot(3, 3, idx + 1)

        history = get_category_history(transactions, category, months_back=12, base_date=report_month_start)
        months = list(history.keys())
        amounts = list(history.values())

        # Line plot with trend
        ax.plot(months, amounts, marker='o', linewidth=2, markersize=6, label='Spending')
        ax.fill_between(range(len(months)), amounts, alpha=0.3)

        # Add average line
        avg = sum(amounts) / len(amounts) if amounts else 0
        ax.axhline(y=avg, color='r', linestyle='--', alpha=0.5, label='Average')

        ax.set_title(f'{category}', fontweight='bold', fontsize=10)
        ax.set_xlabel('Month', fontsize=8)
        ax.set_ylabel('Spending (£)', fontsize=8)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    # Use last subplot for category comparison if we have < 9 categories
    if len(sorted_categories) < 9:
        ax_summary = plt.subplot(3, 3, 9)

        # Sort categories by current month's spending for the bar chart
        sorted_categories.sort(key=lambda x: x[1])

        # Show all top categories as horizontal bar
        all_cats = [cat for cat, _ in sorted_categories]
        all_amounts = [amt for _, amt in sorted_categories]

        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(all_cats)))
        ax_summary.barh(all_cats, all_amounts, color=colors)
        ax_summary.set_xlabel(f'{report_month_start.strftime("%B %Y")} Spending (£)', fontsize=8)
        ax_summary.set_title(f'Category Comparison ({report_month_start.strftime("%B %Y")})', fontweight='bold', fontsize=10)
        ax_summary.tick_params(axis='both', labelsize=7)
        ax_summary.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, "02_category_deep_dive.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n💾 Saved: {output_path}")