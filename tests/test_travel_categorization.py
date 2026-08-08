# tests/test_travel_categorization.py
import unittest
import os
import yaml
from datetime import date
from spending_tracker.categorization import categorize_transaction

class TestTravelCategorization(unittest.TestCase):

    def setUp(self):
        """Set up dummy data for travel categorization tests."""
        self.category_map = {"Groceries": ["Tesco"]}
        self.travel_destinations = {
            'trips': [{
                'destination': 'Test Trip',
                'start_date': date(2025, 6, 10),
                'end_date': date(2025, 6, 20)
            }]
        }

    def test_transaction_within_travel_period(self):
        """Test that a transaction within a travel period is categorized as Travel."""
        transaction = {
            "date": date(2025, 6, 15),
            "description": "Some restaurant",
            "amount": -50.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations)
        self.assertEqual(category, "Travel")

    def test_transaction_outside_travel_period(self):
        """Test that a transaction outside a travel period is Uncategorized."""
        transaction = {
            "date": date(2025, 7, 1),
            "description": "Some shop",
            "amount": -25.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations)
        self.assertEqual(category, "Uncategorized")

    def test_keyword_categorization_takes_precedence(self):
        """Test that keyword-based categorization happens before travel-based categorization."""
        transaction = {
            "date": date(2025, 6, 15), # Within travel period
            "description": "Tesco superstore", # Matches a keyword
            "amount": -30.00
        }
        category = categorize_transaction(transaction, self.category_map, self.travel_destinations)
        self.assertEqual(category, "Groceries")

if __name__ == '__main__':
    unittest.main()
