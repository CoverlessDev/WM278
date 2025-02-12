from flask import Flask, render_template
from flask.views import MethodView

app = Flask(__name__)

# Sample inventory data
inventory = [
    #this will be handled with a JSON
]

class HomePage(MethodView):
    def get(self):
        # Render the main landing page with inventory information
        return render_template('pages/index.html', inventory=inventory)

class InventoryPage(MethodView):
    def get(self):
        # Render the inventory tracking page
        return render_template('pages/inventory.html', inventory=inventory)

class PurchasePage(MethodView):
    def get(self):
        # Render the purchasing page
        return render_template('pages/purchase.html')

class ManagementPage(MethodView):
    def get(self):
        # Render the management page for authorised users
        return render_template('pages/management.html')

# URL route mappings using as_view to register the class-based views
app.add_url_rule('/', view_func=HomePage.as_view('home'))
app.add_url_rule('/inventory', view_func=InventoryPage.as_view('inventory'))
app.add_url_rule('/purchase', view_func=PurchasePage.as_view('purchase'))
app.add_url_rule('/management', view_func=ManagementPage.as_view('management'))

if __name__ == '__main__':
    app.run(debug=True)
