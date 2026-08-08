# reporting_text.py
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict

def generate_textual_report(transactions, output_dir, base_date=None):
    """
    Generates structured text files (Markdown and JSON) summarizing spending data
    and visual analytics for LLM consumption.
    """
    if base_date is None:
        base_date = datetime.now().date()

    # Determine reporting month
    if base_date.day < 15:
        current_month_start = (base_date.replace(day=1) - relativedelta(days=1)).replace(day=1)
    else:
        current_month_start = base_date.replace(day=1)

    current_month_end = current_month_start + relativedelta(months=1)
    prev_month_start = current_month_start - relativedelta(months=1)
    prev_month_end = current_month_start
    year_ago_start = current_month_start - relativedelta(years=1)
    year_ago_end = year_ago_start + relativedelta(months=1)

    # Calculate Period Totals & Category Breakdowns
    def get_period_data(start, end):
        cat_spending = defaultdict(float)
        total = 0.0
        for t in transactions:
            if start <= t['date'] < end and t['amount'] < 0:
                amt = abs(t['amount'])
                cat_spending[t['category']] += amt
                total += amt
        return dict(cat_spending), total

    curr_cats, curr_total = get_period_data(current_month_start, current_month_end)
    prev_cats, prev_total = get_period_data(prev_month_start, prev_month_end)
    yoy_cats, yoy_total = get_period_data(year_ago_start, year_ago_end)

    # 12-Month Historical Monthly Trend Data (aligned with current reporting month)
    months_back = 12
    monthly_trends = {}
    months_list = []
    for i in range(months_back - 1, -1, -1):
        m_start = current_month_start - relativedelta(months=i)
        m_end = m_start + relativedelta(months=1)
        m_str = m_start.strftime('%Y-%m')
        months_list.append(m_str)
        cats, tot = get_period_data(m_start, m_end)
        monthly_trends[m_str] = {
            "total_spent": round(tot, 2),
            "by_category": {c: round(a, 2) for c, a in sorted(cats.items(), key=lambda x: x[1], reverse=True)}
        }


    # Top Merchant Breakdown for Current Month
    merchant_spending = defaultdict(float)
    for t in transactions:
        if current_month_start <= t['date'] < current_month_end and t['amount'] < 0:
            merchant_spending[t['description']] += abs(t['amount'])
    top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:15]

    # Structure Data for JSON Export
    report_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "reporting_period": current_month_start.strftime('%B %Y'),
            "start_date": str(current_month_start),
            "end_date": str(current_month_end)
        },
        "executive_summary": {
            "current_month_total": round(curr_total, 2),
            "prev_month_total": round(prev_total, 2),
            "mom_change_percentage": round(((curr_total - prev_total) / prev_total * 100), 2) if prev_total > 0 else 0.0,
            "same_month_last_year_total": round(yoy_total, 2),
            "yoy_change_percentage": round(((curr_total - yoy_total) / yoy_total * 100), 2) if yoy_total > 0 else 0.0,
        },
        "current_month_categories": {c: round(a, 2) for c, a in sorted(curr_cats.items(), key=lambda x: x[1], reverse=True)},
        "top_merchants_current_month": [{"merchant": m, "amount": round(a, 2)} for m, a in top_merchants],
        "monthly_history_12m": monthly_trends
    }

    # Save JSON file
    json_path = os.path.join(output_dir, "llm_report_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # Generate Markdown Summary File
    md_lines = [
        f"# Financial Spending Summary ({current_month_start.strftime('%B %Y')})",
        f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n",
        "## Executive Overview",
        f"- **Current Month Spending**: £{curr_total:,.2f}",
        f"- **Previous Month Spending**: £{prev_total:,.2f} ({'+' if curr_total >= prev_total else ''}{report_data['executive_summary']['mom_change_percentage']}%)",
        f"- **Same Month Last Year Spending**: £{yoy_total:,.2f} ({'+' if curr_total >= yoy_total else ''}{report_data['executive_summary']['yoy_change_percentage']}%)",
        "\n## Current Month Category Breakdown",
        "| Category | Total (£) | % of Total |",
        "| :--- | :--- | :--- |"
    ]

    for cat, amt in sorted(curr_cats.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / curr_total * 100) if curr_total > 0 else 0.0
        md_lines.append(f"| {cat} | £{amt:,.2f} | {pct:.1f}% |")

    md_lines.extend([
        "\n## Top 15 Merchants (Current Month)",
        "| Merchant / Description | Amount (£) |",
        "| :--- | :--- |"
    ])
    for m, a in top_merchants:
        md_lines.append(f"| {m} | £{a:,.2f} |")

    md_lines.extend([
        "\n## 12-Month Monthly Spending Trends",
        "| Month | Total Spent (£) | Top Category | Top Category Spent (£) |",
        "| :--- | :--- | :--- | :--- |"
    ])
    for m_str in months_list:
        mData = monthly_trends[m_str]
        tot = mData["total_spent"]
        if mData["by_category"]:
            top_c, top_a = list(mData["by_category"].items())[0]
        else:
            top_c, top_a = "N/A", 0.0
        md_lines.append(f"| {m_str} | £{tot:,.2f} | {top_c} | £{top_a:,.2f} |")

    md_path = os.path.join(output_dir, "llm_report_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"📝 Textual reports generated:")
    print(f"   - Markdown: {md_path}")
    print(f"   - Structured JSON: {json_path}")
