import json
from flask import Flask, render_template, request, send_file
from flask.views import MethodView
from datetime import datetime
import os
import io

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


def log_stock_change(product_name, season, old_stock, new_stock):
    log_entry = {
        "product_name": product_name,
        "season": season,
        "old_stock": old_stock,
        "new_stock": new_stock,
        "timestamp": datetime.now().isoformat()
    }
    log_file_path = 'static/jsons/stock_changes_log.JSON'
    if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
        with open(log_file_path, 'r') as log_file:
            log_data = json.load(log_file)
    else:
        log_data = []

    log_data.append(log_entry)

    with open(log_file_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)


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
        product_found = False
        new_product = None  # Initialize new_product

        for product in inventory:
            if product['type_of_plant'] == selected_product:
                old_stock = product['stock']
                new_stock = old_stock + amount
                product['stock'] = new_stock  # Update the stock
                log_stock_change(selected_product, product['season'], old_stock, new_stock)  # Log the change
                product_found = True
                break

        if not product_found:
            # If the product is not found, add it to the inventory
            new_product = {
                "type_of_plant": selected_product,
                "season": "unknown",  # You can set a default season or get it from the form
                "price": 0,  # Set a default price or get it from the form
                "stock": amount
            }
            inventory.append(new_product)
            log_stock_change(selected_product, "unknown", 0, amount)  # Log the new product addition

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
            else:
                # If the product is not found in the season file, add it
                if new_product:
                    season_inventory.append(new_product)

            with open(file_path, 'w') as f:
                json.dump(season_inventory, f, indent=4)

        return render_template('pages/purchase.html', inventory=inventory)


class InventoryReportPage(MethodView):
    def get(self):
        inventory = load_all_inventory()
        low_stock_items = [item for item in inventory if item['stock'] < 10]
        total_stock = sum(item['stock'] for item in inventory)
        total_price = sum(item['stock'] * item['price'] for item in inventory)
        total_price = round(total_price, 2)
        return render_template('pages/inventory_report.html', inventory=inventory, low_stock_items=low_stock_items,
                               total_stock=total_stock, total_price=total_price)


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


@app.route('/download_inventory_report')
def download_inventory_report():
    inventory = load_all_inventory()
    report_content = "Type of Plant,Season,Price,Stock\n"
    for item in inventory:
        report_content += f"{item['type_of_plant']},{item['season']},{item['price']},{item['stock']}\n"

    report_file = io.StringIO(report_content)
    return send_file(io.BytesIO(report_file.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='inventory_report.csv')


@app.route('/inventory_tracking')
def inventory_tracking():
    inventory = load_all_inventory()
    return render_template('pages/inventory_tracking.html', inventory=inventory)


app.add_url_rule('/', view_func=HomePage.as_view('home'))
app.add_url_rule('/product/<season>/<product_name>', view_func=ProductPage.as_view('product'))
app.add_url_rule('/management', view_func=ManagementPage.as_view('management'))
app.add_url_rule('/profile', view_func=ProfilePage.as_view('profile'))
app.add_url_rule('/dashboard', view_func=DashboardPage.as_view('dashboard'))
app.add_url_rule('/purchase', view_func=PurchasePage.as_view('purchase'), methods=['GET', 'POST'])
app.add_url_rule('/inventory_report', view_func=InventoryReportPage.as_view('inventory_report'))

if __name__ == '__main__':
    app.run(debug=True)
