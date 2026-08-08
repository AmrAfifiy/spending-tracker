# tests/test_date_based_categorization.py
import unittest
import os
import yaml
from datetime import date
from spending_tracker.categorization import categorize_transaction

class TestDateBasedCategorization(unittest.TestCase):

    def setUp(self):
        """Set up dummy data for date-based categorization tests."""
        self.category_map = {"Groceries": ["Tesco"]}
        self.travel_destinations = {
            'trips': [{
                'destination': 'Test Trip',
                'start_date': date(2025, 6, 10),
                'end_date': date(2025, 6, 20)
            }]
        }
        self.date_based_rules = {
            'date_based_rules': [
                {
                    'description_contains': "generic payment",
                    'date': "2025-01-15",
                    'category': "Specific Service"
                },
                {
                    'description_contains': "monthly fee",
                    'month': "2",
                    'category': "Subscription"
                },
                {
                    'description_contains': "daily charge",
                    'day': "5",
                    'category': "Daily Fee"
                }
            ]
        }

    def test_full_date_match(self):
        """Test categorization by full date match."""
        transaction = {
            "date": date(2025, 1, 15),
            "description": "generic payment for something",
            "amount": -10.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations, self.date_based_rules)
        self.assertEqual(category, "Specific Service")

    def test_month_match(self):
        """Test categorization by month match."""
        transaction = {
            "date": date(2025, 2, 10),
            "description": "monthly fee",
            "amount": -5.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations, self.date_based_rules)
        self.assertEqual(category, "Subscription")

    def test_day_match(self):
        """Test categorization by day match."""
        transaction = {
            "date": date(2025, 3, 5),
            "description": "some daily charge",
            "amount": -2.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations, self.date_based_rules)
        self.assertEqual(category, "Daily Fee")

    def test_date_based_precedence(self):
        """Test that date-based rules take precedence over other rules."""
        # This transaction matches a date-based rule, a keyword rule, and a travel rule
        transaction = {
            "date": date(2025, 6, 15),
            "description": "Tesco - generic payment", # Matches keyword and date-based rule
            "amount": -10.00
        }
        # A new date-based rule for this test
        date_rules = {
            'date_based_rules': [{
                'description_contains': "generic payment",
                'date': "2025-06-15",
                'category': "Specific Holiday Purchase"
            }]
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations, date_rules)
        self.assertEqual(category, "Specific Holiday Purchase")

if __name__ == '__main__':
    unittest.main()
