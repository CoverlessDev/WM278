import unittest
import json
from unittest.mock import patch, mock_open
from app import app, load_inventory, load_product, log_stock_change, is_logged_in

# Dummy data for testing
dummy_credentials = {
    "admin": [{"username": "testuser", "password": "testpass"}]
}

dummy_inventory = [
    {"type_of_plant": "Aloe Vera", "season": "summer", "price": 15.99, "stock": 10}
]

dummy_sales = [
    {"product_name": "Aloe Vera", "quantity_sold": 2}
]

dummy_stock_changes = [
    {"product_name": "Aloe Vera", "season": "summer", "old_stock": 10, "new_stock": 12,
     "timestamp": "2023-01-01T00:00:00"}
]


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        app.testing = True
        self.client = app.test_client()

    def test_load_inventory(self):
        # Test loading inventory for a specific season using dummy data
        season = 'summer'
        data_str = json.dumps(dummy_inventory)
        with patch("builtins.open", mock_open(read_data=data_str)) as mocked_file:
            inventory = load_inventory(season)
            self.assertEqual(inventory, dummy_inventory)
            mocked_file.assert_called_with(f'static/jsons/{season}flowers.JSON')

    def test_load_product_found(self):
        # Test loading a product that exists in the inventory
        season = 'summer'
        data_str = json.dumps(dummy_inventory)
        with patch("builtins.open", mock_open(read_data=data_str)):
            product = load_product(season, "Aloe Vera")
            self.assertIsNotNone(product)
            self.assertEqual(product["type_of_plant"], "Aloe Vera")

    def test_load_product_not_found(self):
        # Test loading a product that does not exist in the inventory
        season = 'summer'
        data_str = json.dumps(dummy_inventory)
        with patch("builtins.open", mock_open(read_data=data_str)):
            product = load_product(season, "NonExistentPlant")
            self.assertIsNone(product)

    def test_log_stock_change(self):
        # Test logging a stock change entry
        product_name = "Aloe Vera"
        season = "summer"
        old_stock = 10
        new_stock = 15

        # Simulate file not existing (or empty file)
        m = mock_open(read_data="")
        with patch("os.path.exists", return_value=False), \
                patch("builtins.open", m) as mocked_file:
            log_stock_change(product_name, season, old_stock, new_stock)
            # Ensure file was opened in write mode after logging
            mocked_file.assert_called_with('static/jsons/stock_changes_log.JSON', 'w')

    def test_is_logged_in(self):
        # Test checking if a user is logged in
        data_str = json.dumps(dummy_credentials)
        with patch("builtins.open", mock_open(read_data=data_str)):
            with app.test_request_context():
                from flask import session
                session['user'] = "testuser"
                result = is_logged_in()
                self.assertTrue(result)
                self.assertEqual(session.get('role'), "admin")

    def test_login_get(self):
        # Test GET request to the login page
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<form', response.data)

    def test_home_redirects_when_not_logged_in(self):
        # Test redirect to login page when accessing home page without login
        response = self.client.get('/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers.get("Location", ""))

    def test_api_inventory(self):
        # Test API endpoint for retrieving inventory data
        dummy_all_inventory = dummy_inventory  # For simplicity
        data_str = json.dumps(dummy_all_inventory)
        with patch("builtins.open", mock_open(read_data=data_str)):
            response = self.client.get('/api/inventory')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIsInstance(data, list)

    def test_search(self):
        # Test search functionality with a query that matches an inventory item
        data_str = json.dumps(dummy_inventory)
        with patch("builtins.open", mock_open(read_data=data_str)):
            response = self.client.get('/search?query=aloe')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Aloe Vera", response.data)

    def test_logout(self):
        # Test logout functionality
        with app.test_request_context():
            from flask import session
            session['user'] = "testuser"
            response = self.client.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            response_home = self.client.get('/', follow_redirects=False)
            self.assertEqual(response_home.status_code, 302)
            self.assertIn("/login", response_home.headers.get("Location", ""))


if __name__ == '__main__':
    unittest.main()