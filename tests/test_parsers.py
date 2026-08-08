# test_parsers.py
import unittest
import os
import csv
from datetime import date, datetime
from spending_tracker.parsers import parse_barclays_csv, parse_monzo_csv, parse_revolut_csv, parse_amex_csv, parse_barclays_card_raw

class TestParsers(unittest.TestCase):

    def setUp(self):
        """Set up dummy CSV files for testing all parsers."""
        self.test_files = []

        # Barclays CSV
        self.barclays_csv_path = "test_barclays.csv"
        with open(self.barclays_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Number", "Date", "Account", "Amount", "Subcategory", "Memo"])
            writer.writerow(["0", "15/12/2025", "20-10-53 60902160", "-50.25", "Card Purchase", "Tesco Transaction"])
            writer.writerow(["0", "14/12/2025", "20-10-53 60902160", "-12.99", "Card Purchase", "Amazon Purchase"])
            writer.writerow(["0", "13/12/2025", "20-10-53 60902160", "100.00", "Funds Transfer", "Deposit"])
        self.test_files.append(self.barclays_csv_path)

        # Monzo CSV
        self.monzo_csv_path = "test_monzo.csv"
        with open(self.monzo_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Transaction ID", "Date", "Time", "Type", "Name", "Emoji", "Category", "Amount", "Currency", "Local amount", "Local currency", "Notes and #tags", "Address", "Receipt", "Description", "Category split", "Money Out", "Money In"])
            writer.writerow(["tx_1", "01/01/2025", "10:00:00", "Card payment", "Starbucks", "☕️", "Eating Out", "-5.50", "GBP", "-5.50", "GBP", "", "", "", "", "", "-5.50", ""])
            writer.writerow(["tx_2", "02/01/2025", "11:00:00", "Faster payment", "Salary", "💰", "Income", "1500.00", "GBP", "1500.00", "GBP", "", "", "", "", "", "", "1500.00"])
            writer.writerow(["tx_3", "03/01/2025", "12:00:00", "Card payment", "Tesco", "🛒", "Groceries", "-23.75", "GBP", "-23.75", "GBP", "", "", "", "", "", "-23.75", ""])
        self.test_files.append(self.monzo_csv_path)

        # Revolut CSV
        self.revolut_csv_path = "test_revolut.csv"
        with open(self.revolut_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Product", "Started Date", "Completed Date", "Description", "Amount", "Fee", "Currency", "State", "Balance"])
            writer.writerow(["Card Payment", "Current", "2025-01-05 10:30:00", "2025-01-05 10:30:00", "Restaurant Bill", "-30.00", "0.00", "GBP", "COMPLETED", "100.00"])
            writer.writerow(["Transfer", "Current", "2025-01-06 11:00:00", "2025-01-06 11:00:00", "Deposit", "200.00", "0.00", "GBP", "COMPLETED", "300.00"])
            writer.writerow(["Card Payment", "Current", "2025-01-07 12:00:00", "2025-01-07 12:00:00", "Online Shopping", "-15.50", "0.00", "GBP", "REVERTED", "284.50"]) # Should be skipped
        self.test_files.append(self.revolut_csv_path)

        # Amex CSV
        self.amex_csv_path = "test_amex.csv"
        with open(self.amex_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Description", "Amount", "Extended Details", "Appears On Your Statement As", "Address", "Town/City", "Postcode", "Country", "Reference", "Category"])
            writer.writerow(["10/01/2025", "TESCO SUPERSTORE", "45.00", "", "TESCO SUPERSTORE", "", "", "", "", "", "Groceries"])
            writer.writerow(["11/01/2025", "COFFEE SHOP", "5.20", "", "COFFEE SHOP", "", "", "", "", "", "Eating Out"])
            writer.writerow(["12/01/2025", "PAYMENT RECEIVED - THANK YOU", "-1000.00", "", "PAYMENT RECEIVED - THANK YOU", "", "", "", "", "", ""]) # Should be skipped
        self.test_files.append(self.amex_csv_path)

        # Barclays Card Raw Txt
        self.barclays_card_raw_path = "test_barclays_card_raw.txt"
        with open(self.barclays_card_raw_path, 'w') as f:
            f.write("#2024\n")
            f.write("01 Jan Amazon Prime*V01As3OT5, Amzn.Co.UK/PM £8.99\n")
            f.write("03 Aug Amznmktplace, Amazon.co.uk £23.98CR\n")
            f.write("#2025\n")
            f.write("02 Jan Trainline, +443332022222 £10.65\n")
        self.test_files.append(self.barclays_card_raw_path)

    def tearDown(self):
        """Remove all dummy CSV files."""
        for f_path in self.test_files:
            if os.path.exists(f_path):
                os.remove(f_path)

    def test_parse_barclays_csv(self):
        """Test parsing of a Barclays CSV file."""
        transactions = parse_barclays_csv(self.barclays_csv_path)
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0]['date'], date(2025, 12, 15))
        self.assertEqual(transactions[0]['description'], 'Tesco Transaction')
        self.assertEqual(transactions[0]['amount'], -50.25)
        self.assertEqual(transactions[2]['description'], 'Deposit')
        self.assertEqual(transactions[2]['amount'], 100.00)

    def test_parse_monzo_csv(self):
        """Test parsing of a Monzo CSV file."""
        transactions = parse_monzo_csv(self.monzo_csv_path)
        self.assertEqual(len(transactions), 3)
        self.assertEqual(transactions[0]['date'], date(2025, 1, 1))
        self.assertEqual(transactions[0]['description'], 'Starbucks')
        self.assertEqual(transactions[0]['amount'], -5.50)
        self.assertEqual(transactions[1]['description'], 'Salary')
        self.assertEqual(transactions[1]['amount'], 1500.00)

    def test_parse_revolut_csv(self):
        """Test parsing of a Revolut CSV file."""
        transactions = parse_revolut_csv(self.revolut_csv_path)
        self.assertEqual(len(transactions), 2) # One transaction should be skipped due to REVERTED state
        self.assertEqual(transactions[0]['date'], date(2025, 1, 5))
        self.assertEqual(transactions[0]['description'], 'Restaurant Bill')
        self.assertEqual(transactions[0]['amount'], -30.00)
        self.assertEqual(transactions[1]['description'], 'Deposit')
        self.assertEqual(transactions[1]['amount'], 200.00)

    def test_parse_barclays_csv_with_filtering(self):
        """Test parsing of a Barclays CSV file with filtering."""
        filter_rules = ["amazon"]
        transactions = parse_barclays_csv(self.barclays_csv_path, filter_rules=filter_rules)
        self.assertEqual(len(transactions), 2)
        descriptions = [t['description'] for t in transactions]
        self.assertNotIn('Amazon Purchase', descriptions)

    def test_parse_monzo_csv_with_filtering(self):
        """Test parsing of a Monzo CSV file with filtering."""
        filter_rules = ["salary"]
        transactions = parse_monzo_csv(self.monzo_csv_path, filter_rules=filter_rules)
        self.assertEqual(len(transactions), 2)
        descriptions = [t['description'] for t in transactions]
        self.assertNotIn('Salary', descriptions)

    def test_parse_revolut_csv_with_filtering(self):
        """Test parsing of a Revolut CSV file with filtering."""
        filter_rules = ["deposit"]
        transactions = parse_revolut_csv(self.revolut_csv_path, filter_rules=filter_rules)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['description'], 'Restaurant Bill')

    def test_parse_amex_csv_with_filtering(self):
        """Test parsing of an Amex CSV file with filtering."""
        filter_rules = ["coffee shop", "PAYMENT RECEIVED - THANK YOU"]
        transactions = parse_amex_csv(self.amex_csv_path, filter_rules=filter_rules)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['description'], 'TESCO SUPERSTORE')

    def test_parse_barclays_card_raw(self):
        """Test parsing of a Barclays Card raw text file."""
        transactions = parse_barclays_card_raw(self.barclays_card_raw_path)
        self.assertEqual(len(transactions), 3)

        self.assertEqual(transactions[0]['date'], date(2024, 1, 1))
        self.assertEqual(transactions[0]['description'], 'Amazon Prime*V01As3OT5, Amzn.Co.UK/PM')
        self.assertEqual(transactions[0]['amount'], -8.99)

        self.assertEqual(transactions[1]['date'], date(2024, 8, 3))
        self.assertEqual(transactions[1]['description'], 'Amznmktplace, Amazon.co.uk')
        self.assertEqual(transactions[1]['amount'], 23.98)

        self.assertEqual(transactions[2]['date'], date(2025, 1, 2))
        self.assertEqual(transactions[2]['description'], 'Trainline, +443332022222')
        self.assertEqual(transactions[2]['amount'], -10.65)

if __name__ == '__main__':
    unittest.main()