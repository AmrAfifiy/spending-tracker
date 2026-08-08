import csv
from datetime import datetime
import yaml
import re

def load_filter_rules(filepath="config/filter_rules.yml"):
    """Loads the filtering rules from a YAML file."""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def parse_barclays_csv(filepath, filter_rules=None):
    """Parses a Barclays CSV file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            if not row:  # Skip empty rows
                continue

            if len(row) >= 6:
                try:
                    description = re.sub(r'\s+', ' ', row[5].strip())
                    if any(keyword.lower() in description.lower() for keyword in filter_rules):
                        continue

                    date_str = row[1].strip()
                    amount_str = row[3].strip()

                    transactions.append({
                        "date": datetime.strptime(date_str, '%d/%m/%Y').date(),
                        "description": description,
                        "amount": float(amount_str),
                    })
                except (ValueError, IndexError) as e:
                    print(f"Skipping row due to parsing error: {row} - {e}")
                    continue
    return transactions

def parse_barclays_card_csv(filepath, filter_rules=None):
    """Parses a Barclays Card CSV file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            if not row or len(row) < 7:  # Skip empty or short rows
                continue

            try:
                description = re.sub(r'\s+', ' ', row[1].strip())
                if any(keyword.lower() in description.lower() for keyword in filter_rules):
                    continue

                date_str = row[0].strip()
                credit_str = row[5].strip().replace('"', '')
                debit_str = row[6].strip().replace('"', '')
                
                if credit_str:
                    continue # Ignore credit transactions

                amount = 0.0
                if debit_str:
                    amount = -float(debit_str.replace(',', ''))
                else:
                    continue # Skip if no amount

                transactions.append({
                    "date": datetime.strptime(date_str, '%d %b %y').date(),
                    "description": description,
                    "amount": amount,
                })
            except (ValueError, IndexError) as e:
                print(f"Skipping row due to parsing error: {row} - {e}")
                continue
    return transactions
def parse_monzo_csv(filepath, filter_rules=None):
    """Parses a Monzo CSV file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                description = re.sub(r'\s+', ' ', (row['Description'].strip() if row['Description'] else row['Name'].strip()))
                if any(keyword.lower() in description.lower() for keyword in filter_rules):
                    continue

                date_str = row['Date'].strip()
                amount_str = row['Amount'].strip()

                transactions.append({
                    "date": datetime.strptime(date_str, '%d/%m/%Y').date(),
                    "description": description,
                    "amount": float(amount_str),
                })
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to parsing error: {row} - {e}")
                continue
    return transactions

def parse_revolut_csv(filepath, filter_rules=None):
    """Parses a Revolut CSV file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['State'].upper() == 'COMPLETED':
                try:
                    description = re.sub(r'\s+', ' ', row['Description'].strip())
                    if any(keyword.lower() in description.lower() for keyword in filter_rules):
                        continue

                    transactions.append({
                        "date": datetime.strptime(row['Started Date'], '%Y-%m-%d %H:%M:%S').date(),
                        "description": description,
                        "amount": float(row['Amount']),
                    })
                except (ValueError, KeyError) as e:
                    print(f"Skipping row due to parsing error: {row} - {e}")
                    continue
    return transactions

def parse_amex_csv(filepath, filter_rules=None):
    """Parses an American Express CSV file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            description = re.sub(r'\s+', ' ', row['Description'].strip())
            if any(keyword.lower() in description.lower() for keyword in filter_rules):
                continue

            try:
                date_str = row['Date'].strip()
                amount_str = row['Amount'].strip()

                amount = -float(amount_str)

                transactions.append({
                    "date": datetime.strptime(date_str, '%d/%m/%Y').date(),
                    "description": description,
                    "amount": amount,
                })
            except (ValueError, KeyError) as e:
                print(f"Skipping row due to parsing error: {row} - {e}")
                continue
    return transactions

def parse_barclays_card_raw(filepath, filter_rules=None):
    """Parses a Barclays Card raw text file and returns a list of transactions."""
    if filter_rules is None:
        filter_rules = []
    transactions = []
    current_year = None
    transaction_regex = re.compile(r"^(\d{2}\s\w{3})\s+(.*?)\s+£([\d,]+\.\d{2})(CR)?$")


    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith('#'):
                try:
                    current_year = int(line[1:])
                except ValueError:
                    continue # Ignore if it's not a valid year
                continue

            if not current_year:
                continue # Skip transactions until a year is set

            match = transaction_regex.match(line)
            if match:
                date_str, raw_description, amount_str, is_credit_str = match.groups()
                description = re.sub(r'\s+', ' ', raw_description.strip())

                if any(keyword.lower() in description.lower() for keyword in filter_rules):
                    continue

                try:
                    date_obj = datetime.strptime(f"{date_str} {current_year}", "%d %b %Y").date()
                    amount = float(amount_str.replace(',', ''))
                    if not is_credit_str:
                        amount = -amount

                    transactions.append({
                        "date": date_obj,
                        "description": description.strip(),
                        "amount": amount,
                    })
                except ValueError as e:
                    print(f"Skipping row due to parsing error: {line} - {e}")
                    continue
            else:
                print(f"Skipping row due to parsing error: {line} - {e}")
    return transactions


def get_parser(bank_name):
    """Returns the appropriate parser for the given bank name."""
    if bank_name.lower() == 'barclays':
        return parse_barclays_csv
    elif bank_name.lower() == 'monzo':
        return parse_monzo_csv
    elif bank_name.lower() == 'revolut_usd' or bank_name.lower() == 'revolut_gbp':
        return parse_revolut_csv
    elif bank_name.lower() == 'amex':
        return parse_amex_csv
    elif bank_name.lower() == 'barclays_card':
        return parse_barclays_card_csv
    else:
        raise ValueError(f"No parser available for bank: {bank_name}")
