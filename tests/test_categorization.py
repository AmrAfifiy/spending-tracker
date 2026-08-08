# tests/test_categorization.py
import unittest
import os
import yaml
from datetime import date
from spending_tracker.categorization import load_category_map, categorize_transaction

class TestCategorization(unittest.TestCase):

    def setUp(self):
        """Set up a dummy categorization map file."""
        self.test_map_path = "test_categorization_map.yml"
        self.initial_map_content = {
            "Groceries": ["Tesco", "Sainsbury's"],
            "Transport": ["TFL", "Uber"],
            "Uncategorized": []
        }
        with open(self.test_map_path, 'w') as f:
            yaml.dump(self.initial_map_content, f)

    def tearDown(self):
        """Remove the dummy categorization map file."""
        if os.path.exists(self.test_map_path):
            os.remove(self.test_map_path)

    def test_load_category_map(self):
        """Test loading the categorization map."""
        loaded_map = load_category_map(self.test_map_path)
        self.assertEqual(loaded_map, self.initial_map_content)

    def test_categorize_transaction(self):
        """Test categorizing a transaction."""
        category_map = load_category_map(self.test_map_path)
        today = date.today()

        # Test with existing categories
        transaction1 = {"description": "Tesco Superstore", "date": today}
        self.assertEqual(categorize_transaction(transaction1, category_map), "Groceries")

        transaction2 = {"description": "Uber ride to work", "date": today}
        self.assertEqual(categorize_transaction(transaction2, category_map), "Transport")

        # Test with case-insensitivity
        transaction3 = {"description": "sainsbury's local", "date": today}
        self.assertEqual(categorize_transaction(transaction3, category_map), "Groceries")

        # Test with uncategorized transaction
        transaction4 = {"description": "Random Shop", "date": today}
        self.assertEqual(categorize_transaction(transaction4, category_map), "Uncategorized")
    
if __name__ == '__main__':
    unittest.main()
