import unittest
import json
from app import app, load_inventory, calculate_metrics, calculate_total_stock, calculate_stock_change, calculate_sales, get_low_stock_items, load_sales_data

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_load_inventory(self):
        season = 'summer'
        inventory = load_inventory(season)
        self.assertIsInstance(inventory, list)
        self.assertGreater(len(inventory), 0)

    def test_calculate_metrics(self):
        metrics = calculate_metrics()
        self.assertIn('total_profit', metrics)
        self.assertIn('amount_of_stock', metrics)
        self.assertIsInstance(metrics['total_profit'], float)
        self.assertIsInstance(metrics['amount_of_stock'], int)

    def test_calculate_total_stock(self):
        total_stock = calculate_total_stock()
        self.assertIsInstance(total_stock, int)
        self.assertGreaterEqual(total_stock, 0)

    def test_calculate_stock_change(self):
        stock_change = calculate_stock_change()
        self.assertIsInstance(stock_change, int)

    def test_calculate_sales(self):
        total_sales = calculate_sales()
        self.assertIsInstance(total_sales, int)
        self.assertGreaterEqual(total_sales, 0)

    def test_get_low_stock_items(self):
        low_stock_items = get_low_stock_items()
        self.assertIsInstance(low_stock_items, list)

    def test_load_sales_data(self):
        sales_data = load_sales_data()
        self.assertIsInstance(sales_data, list)
        self.assertGreater(len(sales_data), 0)

    def test_login(self):
        response = self.app.post('/login', data=dict(
            username='user',
            password='user'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

if __name__ == '__main__':
    unittest.main()