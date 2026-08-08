# categorization.py
import yaml
from datetime import datetime

def load_category_map(filepath="config/categorization_map.yml"):
    """Loads the category mapping from a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def load_travel_destinations(filepath="config/travel_destinations.yml"):
    """Loads the travel destinations and dates from a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def load_date_based_rules(filepath="config/date_based_categorization.yml"):
    """Loads date-based categorization rules from a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def categorize_transaction(transaction, category_map, travel_destinations=None, date_based_rules=None):
    """
    Categorizes a transaction based on its description, and then by travel dates as a fallback.
    """
    description = transaction["description"].lower()
    transaction_date = transaction["date"]

    # 1. Date-based categorization (most specific)
    if date_based_rules:
        for rule in date_based_rules.get('date_based_rules', []):
            if rule.get('description_contains', '').lower() in description:
                rule_date_str = rule.get('date')
                rule_month = rule.get('month')
                rule_day = rule.get('day')
                
                try:
                    if rule_date_str and transaction_date == datetime.strptime(str(rule_date_str), '%Y-%m-%d').date():
                        return rule['category']
                    if rule_month and transaction_date.month == int(rule_month):
                        return rule['category']
                    if rule_day and transaction_date.day == int(rule_day):
                        return rule['category']
                except (ValueError, KeyError) as e:
                    print(f"Warning: Invalid date-based rule: {rule} - {e}. Skipping.")
                    continue
    
    # 2. Keyword-based categorization
    for category, keywords in category_map.items():
        if keywords:
            for keyword in keywords:
                if keyword.lower() in description:
                    return category

    # 3. Travel-based categorization (as a fallback)
    if travel_destinations:
        for trip in travel_destinations.get('trips', []):
            start_date = trip.get('start_date')
            end_date = trip.get('end_date')
            if start_date and end_date:
                try:
                    start_date_obj = datetime.strptime(str(start_date), '%Y-%m-%d').date()
                    end_date_obj = datetime.strptime(str(end_date), '%Y-%m-%d').date()
                    if start_date_obj <= transaction['date'] <= end_date_obj:
                        return "Travel"
                except ValueError:
                    print(f"Warning: Invalid date format for trip: {trip.get('destination')}. Skipping.")
                    continue

    return "Uncategorized"

