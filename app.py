import json
from flask import Flask, render_template, request
from flask.views import MethodView
import os

app = Flask(__name__)

def load_inventory(season):
    file_path = f'static/jsons/{season}flowers.JSON'
    with open(file_path) as f:
        return json.load(f)

def load_product(season, product_name):
    inventory = load_inventory(season)
    for product in inventory:
        if product['type_of_plant'] == product_name:
            return product
    return None

def load_all_inventory():
    seasons = ['summer', 'autumn', 'winter']
    all_inventory = []
    for season in seasons:
        file_path = f'static/jsons/{season}flowers.JSON'
        with open(file_path) as f:
            all_inventory.extend(json.load(f))
    return all_inventory

class HomePage(MethodView):
    def get(self):
        season = request.args.get('season', 'summer')
        inventory = load_inventory(season)
        return render_template('pages/index.html', inventory=inventory, season=season)

class ProductPage(MethodView):
    def get(self, season, product_name):
        product = load_product(season, product_name)
        if product:
            return render_template('pages/product.html', product=product)
        else:
            return "Product not found", 404

class InventoryPage(MethodView):
    def get(self):
        inventory = load_all_inventory()
        return render_template('pages/inventory_tracking.html', inventory=inventory)

class ManagementPage(MethodView):
    def get(self):
        return render_template('pages/management.html')

class ProfilePage(MethodView):
    def get(self):
        return render_template('pages/profile.html', username="John Doe", user_email="john.doe@example.com")

class DashboardPage(MethodView):
    def get(self):
        return render_template('pages/dashboard.html')

class PurchasePage(MethodView):
    def get(self):
        inventory = load_all_inventory()
        return render_template('pages/purchase.html', inventory=inventory)

    def post(self):
        selected_product = request.form['selectedProduct']
        amount = int(request.form['amount'])
        inventory = load_all_inventory()

        for product in inventory:
            if product['type_of_plant'] == selected_product:
                product['stock'] += amount  # Change this line to add to the stock
                break

        # Save the updated inventory back to the JSON files
        seasons = ['summer', 'autumn', 'winter']
        for season in seasons:
            file_path = f'static/jsons/{season}flowers.JSON'
            with open(file_path, 'r') as f:
                season_inventory = json.load(f)

            for product in season_inventory:
                if product['type_of_plant'] == selected_product:
                    product['stock'] += amount  # Update the stock in the JSON data
                    break

            with open(file_path, 'w') as f:
                json.dump(season_inventory, f, indent=4)

        return render_template('pages/purchase.html', inventory=inventory)

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    all_seasons = ['summer', 'autumn', 'winter']
    results = []
    for season in all_seasons:
        inventory = load_inventory(season)
        results.extend([product for product in inventory if query in product['type_of_plant'].lower()])
    return render_template('pages/search_results.html', results=results, query=query)

@app.route('/api/inventory')
def api_inventory():
    inventory = load_all_inventory()
    return json.dumps(inventory)

app.add_url_rule('/', view_func=HomePage.as_view('home'))
app.add_url_rule('/product/<season>/<product_name>', view_func=ProductPage.as_view('product'))
app.add_url_rule('/management', view_func=ManagementPage.as_view('management'))
app.add_url_rule('/profile', view_func=ProfilePage.as_view('profile'))
app.add_url_rule('/dashboard', view_func=DashboardPage.as_view('dashboard'))
app.add_url_rule('/inventory_tracking', view_func=InventoryPage.as_view('inventory_tracking'))
app.add_url_rule('/purchase', view_func=PurchasePage.as_view('purchase'), methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(debug=True)