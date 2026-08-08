# reporting_composition.py
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

def get_category_spending_over_time(transactions, months_back=12, base_date=None):
    """Get spending by category for each month."""
    if base_date is None:
        base_date = datetime.now().date()
        
    monthly_data = {}

    for i in range(months_back - 1, -1, -1):
        month_start = (base_date.replace(day=1) - relativedelta(months=i))
        month_end = month_start + relativedelta(months=1)
        month_str = month_start.strftime('%b %y')

        spending = defaultdict(float)
        for t in transactions:
            if month_start <= t['date'] < month_end and t['amount'] < 0:
                spending[t['category']] += abs(t['amount'])

        monthly_data[month_str] = dict(spending)

    return monthly_data

def get_top_categories_by_average(transactions, top_n=10, months_back=12, base_date=None):
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

    # Sort by average and get top N, excluding specific categories
    sorted_cats = sorted(category_averages.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in sorted_cats if cat not in ['Car', 'Medical & Dental']][:top_n]

def generate_composition_report(transactions, output_dir):
    """Generate category composition analysis showing evolution over time."""

    today = datetime.now().date()

    # Determine the reporting month based on the day of the month
    if today.day < 15:
        # If before the 15th, report on the previous month
        report_month_start = (today.replace(day=1) - relativedelta(days=1)).replace(day=1)
    else:
        # Otherwise, report on the current month
        report_month_start = today.replace(day=1)

    print(f"\n📅 Reporting Month: {report_month_start.strftime('%B %Y')}")
    print("📊 Generating Category Composition Report...")

    months_back = 12
    monthly_data = get_category_spending_over_time(transactions, months_back, base_date=report_month_start)

    if not monthly_data:
        print("No spending data available.")
        return

    # Get top categories by average spending
    top_categories = get_top_categories_by_average(transactions, top_n=10, months_back=months_back, base_date=report_month_start)

    # Prepare data for visualizations
    months = list(monthly_data.keys())

    # Create figure with multiple visualizations
    fig = plt.figure(figsize=(18, 16)) # Increased height for better spacing

    # 1. Stacked Area Chart - Category Composition Over Time
    ax1 = plt.subplot(4, 2, 1)

    # Prepare data for stacking
    category_series = {}
    for cat in top_categories:
        category_series[cat] = [monthly_data[month].get(cat, 0) for month in months]

    # Create stacked area
    x = range(len(months))
    colors = plt.cm.tab20(np.linspace(0, 1, len(top_categories)))

    ax1.stackplot(x, *category_series.values(), labels=category_series.keys(),
                  alpha=0.8, colors=colors)

    ax1.set_xticks(x)
    ax1.set_xticklabels(months, rotation=45, ha='right')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Total Spending (£)')
    ax1.set_title('Category Composition Over Time (Stacked)', fontweight='bold', fontsize=12)
    ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)
    ax1.grid(axis='y', alpha=0.3)

    # 2. Percentage Stacked Area - Relative Composition
    ax2 = plt.subplot(4, 2, 2)

    # Calculate percentages
    totals_per_month = [sum(monthly_data[month].values()) for month in months]
    percentage_series = {}

    for cat in top_categories:
        percentage_series[cat] = [
            (monthly_data[months[i]].get(cat, 0) / totals_per_month[i] * 100) if totals_per_month[i] > 0 else 0
            for i in range(len(months))
        ]

    ax2.stackplot(x, *percentage_series.values(), labels=percentage_series.keys(),
                  alpha=0.8, colors=colors)

    ax2.set_xticks(x)
    ax2.set_xticklabels(months, rotation=45, ha='right')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Percentage of Total (%)')
    ax2.set_title('Category Composition (% of Total)', fontweight='bold', fontsize=12)
    ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=8)
    ax2.set_ylim(0, 100)
    ax2.grid(axis='y', alpha=0.3)

    # 3. Individual Category Trends (Small Multiples) - Top 4
    for idx, cat in enumerate(top_categories[:4]):
        ax = plt.subplot(4, 2, 3 + idx)

        amounts = [monthly_data[month].get(cat, 0) for month in months]
        percentages = [percentage_series[cat][i] for i in range(len(months))]

        # Plot absolute amounts
        color = colors[idx]
        ax_twin = ax.twinx()

        ax.plot(x, amounts, marker='o', linewidth=2, markersize=4,
                color=color, alpha=0.7, label='Amount')
        ax.fill_between(x, amounts, alpha=0.2, color=color)

        # Plot percentages on secondary axis
        ax_twin.plot(x, percentages, marker='s', linewidth=1.5, markersize=3,
                    color='red', alpha=0.5, linestyle='--', label='% of Total')

        ax.set_title(cat, fontweight='bold', fontsize=9)
        ax.set_xticks([0, len(months)//2, len(months)-1])
        ax.set_xticklabels([months[0], months[len(months)//2], months[-1]],
                          rotation=45, ha='right', fontsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax_twin.tick_params(axis='y', labelsize=7)
        ax.set_ylabel('£', fontsize=7, color=color)
        ax_twin.set_ylabel('%', fontsize=7, color='red')
        ax.grid(True, alpha=0.2)

    # 4. Category Share Evolution - Heatmap style
    ax4 = plt.subplot(4, 2, 7)

    # Create matrix for heatmap
    heatmap_data = []
    for cat in top_categories:
        row = [percentage_series[cat][i] for i in range(len(months))]
        heatmap_data.append(row)

    im = ax4.imshow(heatmap_data, aspect='auto', cmap='YlOrRd', interpolation='nearest')

    ax4.set_yticks(range(len(top_categories)))
    ax4.set_yticklabels(top_categories, fontsize=8)
    ax4.set_xticks(range(0, len(months), 2))
    ax4.set_xticklabels([months[i] for i in range(0, len(months), 2)],
                        rotation=45, ha='right', fontsize=8)
    ax4.set_title('Category Share Heatmap (% of Total)', fontweight='bold', fontsize=10)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax4)
    cbar.set_label('% of Total Spending', fontsize=8)

    # 5. Volatility Analysis
    ax5 = plt.subplot(4, 2, 8)

    volatilities = {}
    for cat in top_categories:
        amounts = [monthly_data[month].get(cat, 0) for month in months]
        if amounts and sum(amounts) > 0:
            avg = sum(amounts) / len(amounts)
            std_dev = np.std(amounts)
            cv = (std_dev / avg * 100) if avg > 0 else 0
            volatilities[cat] = cv

    sorted_vol = sorted(volatilities.items(), key=lambda x: x[1], reverse=True)
    vol_cats = [x[0] for x in sorted_vol]
    vol_values = [x[1] for x in sorted_vol]

    colors_vol = ['red' if v > 30 else 'orange' if v > 15 else 'green' for v in vol_values]

    ax5.barh(vol_cats, vol_values, color=colors_vol, alpha=0.7)
    ax5.set_xlabel('Coefficient of Variation (%)', fontsize=9)
    ax5.set_title('Category Spending Volatility', fontweight='bold', fontsize=10)
    ax5.set_xlim(0, max(vol_values) * 1.1 if vol_values else 100)
    ax5.grid(axis='x', alpha=0.3)
    ax5.tick_params(axis='both', labelsize=8)

    # Add volatility legend
    ax5.text(0.98, 0.02, 'Red: High volatility (>30%)\nOrange: Medium (15-30%)\nGreen: Stable (<15%)',
             transform=ax5.transAxes, fontsize=7, va='bottom', ha='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout()

    output_path = os.path.join(output_dir, "03_category_composition.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n💾 Saved: {output_path}")

    # Print insights
    print("\n📈 Key Insights:")

    # Most volatile category
    if volatilities:
        most_volatile = max(volatilities.items(), key=lambda x: x[1])
        least_volatile = min(volatilities.items(), key=lambda x: x[1])
        print(f"  • Most volatile: {most_volatile[0]} (CV: {most_volatile[1]:.1f}%)")
        print(f"  • Most stable: {least_volatile[0]} (CV: {least_volatile[1]:.1f}%)")

    # Growing/shrinking categories
    for cat in top_categories[:3]:
        amounts = [monthly_data[month].get(cat, 0) for month in months]
        if len(amounts) >= 6:
            first_half_avg = sum(amounts[:6]) / 6
            second_half_avg = sum(amounts[6:]) / 6

            if first_half_avg > 0:
                change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
                if abs(change) > 15:
                    trend = "increasing" if change > 0 else "decreasing"
                    print(f"  • {cat}: {trend} by {abs(change):.1f}% (recent vs earlier months)")