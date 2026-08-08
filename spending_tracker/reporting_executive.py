# reporting_executive.py
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from collections import defaultdict

def get_spending_by_period(transactions, start_date, end_date):
    """Get spending data for a specific period."""
    spending = defaultdict(float)
    total_spent = 0

    for t in transactions:
        if start_date <= t['date'] < end_date and t['amount'] < 0:
            cat = t['category']
            amount = abs(t['amount'])
            spending[cat] += amount
            total_spent += amount

    return dict(spending), total_spent

def generate_executive_summary(transactions, output_dir):
    """Generate executive summary with key metrics and overview charts."""

    today = datetime.now().date()

    # Determine the reporting month based on the day of the month
    if today.day < 15:
        # If before the 15th, report on the previous month
        current_month_start = (today.replace(day=1) - relativedelta(days=1)).replace(day=1)
    else:
        # Otherwise, report on the current month
        current_month_start = today.replace(day=1)

    current_month_end = (current_month_start + relativedelta(months=1))

    # Previous month
    prev_month_start = current_month_start - relativedelta(months=1)
    prev_month_end = current_month_start

    # Same month last year
    year_ago_start = current_month_start - relativedelta(years=1)
    year_ago_end = year_ago_start + relativedelta(months=1)

    # Get spending data
    current_spending, current_total = get_spending_by_period(transactions, current_month_start, current_month_end)
    prev_spending, prev_total = get_spending_by_period(transactions, prev_month_start, prev_month_end)
    year_ago_spending, year_ago_total = get_spending_by_period(transactions, year_ago_start, year_ago_end)

    # Print summary
    print(f"\n📅 Current Month: {current_month_start.strftime('%B %Y')}")
    print(f"💷 Total Spending: £{current_total:,.2f}")

    if prev_total > 0:
        change_mom = ((current_total - prev_total) / prev_total) * 100
        print(f"📊 vs Previous Month: {'+' if change_mom >= 0 else ''}£{current_total - prev_total:,.2f} ({'+' if change_mom >= 0 else ''}{change_mom:.1f}%)")

    if year_ago_total > 0:
        change_yoy = ((current_total - year_ago_total) / year_ago_total) * 100
        print(f"📊 vs Same Month Last Year: {'+' if change_yoy >= 0 else ''}£{current_total - year_ago_total:,.2f} ({'+' if change_yoy >= 0 else ''}{change_yoy:.1f}%)")

    # Top spending categories
    if current_spending:
        print(f"\n💳 Top 5 Spending Categories:")
        sorted_cats = sorted(current_spending.items(), key=lambda x: x[1], reverse=True)[:5]
        for i, (cat, amount) in enumerate(sorted_cats, 1):
            percentage = (amount / current_total) * 100
            print(f"  {i}. {cat}: £{amount:,.2f} ({percentage:.1f}%)")

    # Highlights
    print(f"\n✨ Highlights:")
    highlights = []

    # Category changes
    if prev_spending:
        for cat, current_amt in current_spending.items():
            prev_amt = prev_spending.get(cat, 0)
            if prev_amt > 0:
                change_pct = ((current_amt - prev_amt) / prev_amt) * 100
                if abs(change_pct) > 30 and current_amt > 50:  # Significant change and meaningful amount
                    direction = "↑ up" if change_pct > 0 else "↓ down"
                    highlights.append(f"{cat} {direction} {abs(change_pct):.0f}% from last month")

    if highlights:
        for h in highlights[:3]:  # Show top 3 highlights
            print(f"  • {h}")
    else:
        print("  • Spending patterns consistent with previous month")

    # Generate visualizations
    fig = plt.figure(figsize=(16, 10))

    # 1. Current Month Pie Chart
    if current_spending:
        ax1 = plt.subplot(2, 3, 1)

        # Sort categories by amount for the pie chart
        sorted_spending = sorted(current_spending.items(), key=lambda x: x[1], reverse=True)

        cats = [item[0] for item in sorted_spending]
        amounts = [item[1] for item in sorted_spending]

        # Group small categories
        threshold = current_total * 0.02  # Less than 3% goes to "Other"
        main_cats = []
        main_amounts = []
        other_total = 0

        for cat, amt in zip(cats, amounts):
            if amt >= threshold:
                main_cats.append(cat)
                main_amounts.append(amt)
            else:
                other_total += amt

        if other_total > 0:
            main_cats.append("Other")
            main_amounts.append(other_total)

        colors = plt.cm.Set3(range(len(main_cats)))
        ax1.pie(main_amounts, labels=main_cats, autopct='%1.1f%%', startangle=90, colors=colors)
        ax1.set_title(f'Current Month Breakdown\n{current_month_start.strftime("%B %Y")}', fontsize=12, fontweight='bold')

    # 2. Month-over-Month Comparison
    ax2 = plt.subplot(2, 3, 2)
    if prev_spending and current_spending:
        all_cats = sorted(set(list(current_spending.keys()) + list(prev_spending.keys())))
        x = range(len(all_cats))
        width = 0.35

        prev_vals = [prev_spending.get(cat, 0) for cat in all_cats]
        curr_vals = [current_spending.get(cat, 0) for cat in all_cats]

        ax2.bar([i - width/2 for i in x], prev_vals, width, label='Previous Month', alpha=0.8)
        ax2.bar([i + width/2 for i in x], curr_vals, width, label='Current Month', alpha=0.8)

        ax2.set_xlabel('Category')
        ax2.set_ylabel('Amount (£)')
        ax2.set_title('Month-over-Month Comparison', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(all_cats, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)

    # 3. 6-Month Trend
    ax3 = plt.subplot(2, 3, 3)
    months = []
    totals = []

    for i in range(5, -1, -1):
        month_start = current_month_start - relativedelta(months=i)
        month_end = month_start + relativedelta(months=1)
        _, total = get_spending_by_period(transactions, month_start, month_end)
        months.append(month_start.strftime('%b %y'))
        totals.append(total)

    ax3.plot(months, totals, marker='o', linewidth=2, markersize=8)
    ax3.fill_between(range(len(months)), totals, alpha=0.3)
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Total Spending (£)')
    ax3.set_title('6-Month Spending Trend', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)

    # 4. Year-over-Year Comparison
    ax4 = plt.subplot(2, 3, 4)
    if year_ago_total > 0 and current_spending:
        comparison_data = []
        for cat in current_spending.keys():
            curr = current_spending.get(cat, 0)
            prev_yr = year_ago_spending.get(cat, 0)
            if curr > 0 or prev_yr > 0:
                comparison_data.append((cat, prev_yr, curr))

        comparison_data.sort(key=lambda x: x[2], reverse=True)
        comparison_data = comparison_data[:8]  # Top 8 categories

        if comparison_data:
            cats = [x[0] for x in comparison_data]
            prev_yr_vals = [x[1] for x in comparison_data]
            curr_vals = [x[2] for x in comparison_data]

            x = range(len(cats))
            width = 0.35

            ax4.bar([i - width/2 for i in x], prev_yr_vals, width, label='Year Ago', alpha=0.8)
            ax4.bar([i + width/2 for i in x], curr_vals, width, label='Current', alpha=0.8)

            ax4.set_xlabel('Category')
            ax4.set_ylabel('Amount (£)')
            ax4.set_title(f'Year-over-Year Comparison\n{year_ago_start.strftime("%b %Y")} vs {current_month_start.strftime("%b %Y")}', fontweight='bold')
            ax4.set_xticks(x)
            ax4.set_xticklabels(cats, rotation=45, ha='right')
            ax4.legend()
            ax4.grid(axis='y', alpha=0.3)

    # 5. Daily Spending Distribution (Current Month)
    ax5 = plt.subplot(2, 3, 5)
    daily_spending = defaultdict(float)

    for t in transactions:
        if current_month_start <= t['date'] < current_month_end and t['amount'] < 0:
            day = t['date'].day
            daily_spending[day] += abs(t['amount'])

    if daily_spending:
        days = sorted(daily_spending.keys())
        amounts = [daily_spending[d] for d in days]

        ax5.bar(days, amounts, alpha=0.7, color='steelblue')
        ax5.set_xlabel('Day of Month')
        ax5.set_ylabel('Spending (£)')
        ax5.set_title('Daily Spending Pattern (Current Month)', fontweight='bold')
        ax5.grid(axis='y', alpha=0.3)

    # 6. Transaction Count by Category
    ax6 = plt.subplot(2, 3, 6)
    if current_spending:
        transaction_counts = defaultdict(int)
        for t in transactions:
            if current_month_start <= t['date'] < current_month_end and t['amount'] < 0:
                transaction_counts[t['category']] += 1

        sorted_counts = sorted(transaction_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        cats = [x[0] for x in sorted_counts]
        counts = [x[1] for x in sorted_counts]

        ax6.barh(cats, counts, alpha=0.7, color='coral')
        ax6.set_xlabel('Number of Transactions')
        ax6.set_title('Transaction Count by Category', fontweight='bold')
        ax6.grid(axis='x', alpha=0.3)

    plt.tight_layout()

    output_path = os.path.join(output_dir, "01_executive_summary.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n💾 Saved: {output_path}")