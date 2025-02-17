import json
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from flask.views import MethodView
from datetime import datetime
import os
import io

app = Flask(__name__)
app.secret_key = '123456'

# Before each request, reset the session
@app.before_request
def reset_session():
    app.before_request_funcs[None].remove(reset_session)
    clear_session()

# Clear the session
def clear_session():
    session.clear()

# Check if the user is logged in
def is_logged_in():
    if 'user' in session:
        username = session['user']
        with open('static/jsons/credentials.JSON', 'r') as file:
            credentials = json.load(file)
        for role, users in credentials.items():
            if any(user['username'] == username for user in users):
                session['role'] = role  # Store the role in the session
                return True
    return False

# Load inventory for a specific season
def load_inventory(season):
    file_path = f'static/jsons/{season}flowers.JSON'
    with open(file_path) as f:
        return json.load(f)

# Load a specific product from the inventory
def load_product(season, product_name):
    inventory = load_inventory(season)
    for product in inventory:
        if product['type_of_plant'] == product_name:
            return product
    return None

# Calculate metrics for the inventory
def calculate_metrics():
    inventory = load_all_inventory()
    total_profit = sum(item['stock'] * item['price'] for item in inventory)
    amount_of_stock = sum(item['stock'] for item in inventory)
    return {
        "total_profit": round(total_profit, 2),
        "amount_of_stock": amount_of_stock
    }

# Calculate the total stock
def calculate_total_stock():
    inventory = load_all_inventory()
    return sum(item['stock'] for item in inventory)

# Calculate the stock change
def calculate_stock_change():
    log_file_path = 'static/jsons/stock_changes_log.JSON'
    with open(log_file_path, 'r') as log_file:
        log_data = json.load(log_file)

    stock_change = sum(entry['new_stock'] - entry['old_stock'] for entry in log_data)
    return stock_change

# Calculate total sales
def calculate_sales():
    sales_data = load_sales_data()
    total_sales = sum(sale.get('quantity_sold', 0) for sale in sales_data)
    return total_sales

# Get items with low stock
def get_low_stock_items():
    inventory = load_all_inventory()
    return [item['type_of_plant'] for item in inventory if item['stock'] < 10]

# Load sales data
def load_sales_data():
    file_path = 'static/jsons/sales.JSON'
    with open(file_path) as f:
        return json.load(f)

# Load all inventory data
def load_all_inventory():
    seasons = ['summer', 'autumn', 'winter']
    all_inventory = []
    for season in seasons:
        file_path = f'static/jsons/{season}flowers.JSON'
        with open(file_path) as f:
            all_inventory.extend(json.load(f))
    return all_inventory

# Log stock changes
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

# Load user credentials
def load_credentials():
    with open('static/jsons/credentials.JSON', 'r') as file:
        return json.load(file)

# Home page view
class HomePage(MethodView):
    def get(self):
        print("HomePage accessed, session:", session)
        if not is_logged_in():
            return redirect(url_for('login'))
        season = request.args.get('season', 'summer')
        inventory = load_inventory(season)
        return render_template('pages/index.html', inventory=inventory, season=season)

# Product page view
class ProductPage(MethodView):
    def get(self, season, product_name):
        product = load_product(season, product_name)
        if product:
            return render_template('pages/product.html', product=product)
        else:
            return "Product not found", 404

# Inventory page view
class InventoryPage(MethodView):
    def get(self):
        inventory = load_all_inventory()
        return render_template('pages/inventory_tracking.html', inventory=inventory)

# Management page view
class ManagementPage(MethodView):
    def get(self):
        return render_template('pages/management.html')

# Profile page view
class ProfilePage(MethodView):
    def get(self):
        return render_template('pages/profile.html')

# Dashboard page view
class DashboardPage(MethodView):
    def get(self):
        return render_template('pages/dashboard.html')

# Purchase page view
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

# Inventory report page view
class InventoryReportPage(MethodView):
    def get(self):
        inventory = load_all_inventory()
        low_stock_items = [item for item in inventory if item['stock'] < 10]
        total_stock = sum(item['stock'] for item in inventory)
        total_price = sum(item['stock'] * item['price'] for item in inventory)
        total_price = round(total_price, 2)
        return render_template('pages/inventory_report.html', inventory=inventory, low_stock_items=low_stock_items,
                               total_stock=total_stock, total_price=total_price)

# Check login route
@app.route('/check_login')
def check_login():
    if not is_logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('home'))

# Search route
@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    all_seasons = ['summer', 'autumn', 'winter']
    results = []
    for season in all_seasons:
        inventory = load_inventory(season)
        results.extend([product for product in inventory if query in product['type_of_plant'].lower()])
    return render_template('pages/search_results.html', results=results, query=query)

# API route to get inventory data
@app.route('/api/inventory')
def api_inventory():
    inventory = load_all_inventory()
    return json.dumps(inventory)

# API route to get stock changes
@app.route('/api/changes')
def api_changes():
    log_file_path = 'static/jsons/stock_changes_log.JSON'
    with open(log_file_path, 'r') as log_file:
        log_data = json.load(log_file)
    return jsonify(log_data)

# Route to download inventory report
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

# Route to download credentials
@app.route('/download_credentials')
def download_credentials():
    credentials = load_credentials()
    report_content = "Role,Username,Password\n"
    for role, users in credentials.items():
        for user in users:
            report_content += f"{role},{user['username']},{user['password']}\n"

    report_file = io.StringIO(report_content)
    return send_file(io.BytesIO(report_file.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='credentials.csv')

# Route to track inventory
@app.route('/inventory_tracking')
def inventory_tracking():
    inventory = load_all_inventory()
    return render_template('pages/inventory_tracking.html', inventory=inventory)

# API route to get sales data
@app.route('/api/sales_data')
def api_sales_data():
    sales_data = load_sales_data()
    return jsonify(sales_data)

# API route to get top sales data
@app.route('/api/top_sales')
def api_top_sales():
    sales_data = load_sales_data()
    aggregated_sales = {}

    for sale in sales_data:
        product_name = sale['product_name']
        quantity_sold = sale.get('quantity_sold', 0)
        if product_name in aggregated_sales:
            aggregated_sales[product_name] += quantity_sold
        else:
            aggregated_sales[product_name] = quantity_sold

    sorted_sales = sorted(aggregated_sales.items(), key=lambda x: x[1], reverse=True)
    top_sales = [{'product_name': name, 'quantity_sold': quantity} for name, quantity in sorted_sales[:10]]

    return jsonify(top_sales)

# API route to get metrics
@app.route('/api/metrics')
def api_metrics():
    metrics = calculate_metrics()
    return jsonify(metrics)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Load existing credentials
        with open('static/jsons/credentials.JSON', 'r') as file:
            credentials = json.load(file)

        # Check credentials for each role
        for role in credentials:
            for user in credentials[role]:
                if user['username'] == username and user['password'] == password:
                    session['user'] = username  # Store the username in the session
                    session['role'] = role  # Store the role in the session
                    return redirect(url_for('home'))

        return redirect(url_for('login'))

    return render_template('pages/login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# API route to get dashboard metrics
@app.route('/api/dashboard_metrics')
def api_dashboard_metrics():
    total_stock = calculate_total_stock()
    stock_change = calculate_stock_change()
    sales = calculate_sales()
    low_stock_items = get_low_stock_items()
    low_stock_count = len(low_stock_items)

    metrics = {
        "total_stock": total_stock,
        "stock_change": stock_change,
        "sales": sales,
        "low_stock_count": low_stock_count
    }
    return jsonify(metrics)

# Route to display dashboard metrics
@app.route('/dashboard_metrics')
def dashboard_metrics():
    return render_template('resources/dashboard_metrics.html')

# Route to add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    # Load existing credentials
    with open('static/jsons/credentials.JSON', 'r') as file:
        credentials = json.load(file)

    # Ensure the role exists in the credentials
    if role not in credentials:
        credentials[role] = []

    # Add new user
    new_user = {
        "username": username,
        "password": password
    }
    credentials[role].append(new_user)

    # Save updated credentials
    with open('static/jsons/credentials.JSON', 'w') as file:
        json.dump(credentials, file, indent=4)

    return redirect(url_for('management'))

# Route to edit an existing user
@app.route('/edit_user', methods=['POST'])
def edit_user():
    username = request.form['username']
    new_password = request.form['new_password']

    # Load existing credentials
    with open('static/jsons/credentials.JSON', 'r') as file:
        credentials = json.load(file)

    # Find the user and update the password
    for role, users in credentials.items():
        for user in users:
            if user['username'] == username:
                user['password'] = new_password
                break

    # Save updated credentials
    with open('static/jsons/credentials.JSON', 'w') as file:
        json.dump(credentials, file, indent=4)

    return redirect(url_for('management'))

# Route to delete a user
@app.route('/delete_user/<role>/<username>', methods=['POST'])
def delete_user(role, username):
    # Load existing credentials
    with open('static/jsons/credentials.JSON', 'r') as file:
        credentials = json.load(file)

    # Find and remove the user
    if role in credentials:
        credentials[role] = [user for user in credentials[role] if user['username'] != username]

    # Save updated credentials
    with open('static/jsons/credentials.JSON', 'w') as file:
        json.dump(credentials, file, indent=4)

    return redirect(url_for('management'))

# Management page view
@app.route('/management')
def management():
    # Load existing credentials
    with open('static/jsons/credentials.JSON', 'r') as file:
        credentials = json.load(file)
    return render_template('pages/management.html', credentials=credentials)

# Add URL rules for the views
app.add_url_rule('/', view_func=HomePage.as_view('home'))
app.add_url_rule('/product/<season>/<product_name>', view_func=ProductPage.as_view('product'))
app.add_url_rule('/profile', view_func=ProfilePage.as_view('profile'))
app.add_url_rule('/purchase', view_func=PurchasePage.as_view('purchase'), methods=['GET', 'POST'])
app.add_url_rule('/inventory_report', view_func=InventoryReportPage.as_view('inventory_report'))
app.add_url_rule('/dashboard', view_func=DashboardPage.as_view('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)