# spending_tracker/loader.py
import yaml
from datetime import datetime
from . import parsers, categorization, currency

def load_and_categorize_transactions():
    """Loads all transactions from CSVs defined in config.yml and categorizes them."""

    with open('config/config.yml', 'r') as f:
        config = yaml.safe_load(f)

    with open('config/filter_rules.yml', 'r') as f:
        filter_config = yaml.safe_load(f)

    travel_destinations = categorization.load_travel_destinations()
    date_based_rules = categorization.load_date_based_rules()

    base_currency = config.get('base_currency', 'GBP')
    converter = currency.CurrencyConverter(base_currency=base_currency)
    filter_rules = filter_config.get('filters', {})
    category_map = categorization.load_category_map()

    all_transactions = []
    for bank_key, bank_info in config.get('banks', {}).items():
        parser = parsers.get_parser(bank_key)
        bank_filter_rules = filter_rules.get(bank_key, [])

        for filepath in bank_info.get('files', []):
            transactions_data = parser(filepath, filter_rules=bank_filter_rules)
            for t_data in transactions_data:

                currency_code = bank_info.get('currency', base_currency)
                t_data['original_amount'] = t_data['amount']
                t_data['original_currency'] = currency_code
                t_data['bank'] = bank_key

                if currency_code != base_currency:
                    converted_amount = converter.convert(t_data['amount'], currency_code, t_data['date'])
                    if converted_amount is not None:
                        t_data['amount'] = converted_amount
                    else:
                        print(f"Warning: No exchange rate for {currency_code} on {t_data['date'].strftime('%Y-%m-%d')}. Amount not converted.")

                category_name = categorization.categorize_transaction(t_data, category_map, travel_destinations, date_based_rules)
                t_data['category'] = category_name
                all_transactions.append(t_data)

    # Load and apply refund mappings
    import os
    if os.path.exists('config/refund_map.yml'):
        with open('config/refund_map.yml', 'r') as f:
            refund_data = yaml.safe_load(f)
        
        if refund_data and 'refunds' in refund_data:
            excluded_transactions = set()
            for mapping in refund_data['refunds']:
                p_info = mapping.get('purchase')
                r_info = mapping.get('refund')
                if not p_info or not r_info:
                    continue
                
                # Match purchase transaction
                purchase_txn = None
                p_date = datetime.strptime(str(p_info['date']), '%Y-%m-%d').date()
                p_amount = float(p_info['amount'])
                p_bank = p_info['bank']
                p_desc = p_info['description'].lower()
                
                for t in all_transactions:
                    if (t['bank'] == p_bank and 
                        t['date'] == p_date and 
                        abs(t['original_amount'] - p_amount) < 1e-2 and 
                        p_desc in t['description'].lower() and 
                        id(t) not in excluded_transactions):
                        purchase_txn = t
                        break
                
                # Match refund transaction
                refund_txn = None
                r_date = datetime.strptime(str(r_info['date']), '%Y-%m-%d').date()
                r_amount = float(r_info['amount'])
                r_bank = r_info['bank']
                r_desc = r_info['description'].lower()
                
                for t in all_transactions:
                    if (t['bank'] == r_bank and 
                        t['date'] == r_date and 
                        abs(t['original_amount'] - r_amount) < 1e-2 and 
                        r_desc in t['description'].lower() and 
                        id(t) not in excluded_transactions):
                        refund_txn = t
                        break
                
                if purchase_txn and refund_txn:
                    # Offset the amount in the base currency (GBP)
                    purchase_txn['amount'] += refund_txn['amount']
                    excluded_transactions.add(id(refund_txn))
                else:
                    if not purchase_txn:
                        print(f"Warning: Could not find purchase transaction matching {p_info}")
                    if not refund_txn:
                        print(f"Warning: Could not find refund transaction matching {r_info}")
            
            # Exclude the matched refund transactions
            all_transactions = [t for t in all_transactions if id(t) not in excluded_transactions]

    return all_transactions
