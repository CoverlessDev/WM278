import json
from flask import Flask, render_template, request
from flask.views import MethodView

app = Flask(__name__)

def load_inventory(season):
    file_path = f'static/jsons/{season}flowers.JSON'
    with open(file_path) as f:
        return json.load(f)

class HomePage(MethodView):
    def get(self):
        season = request.args.get('season', 'summer')
        inventory = load_inventory(season)
        return render_template('pages/index.html', inventory=inventory, season=season)

class InventoryPage(MethodView):
    def get(self):
        season = request.args.get('season', 'summer')
        inventory = load_inventory(season)
        return render_template('pages/inventory.html', inventory=inventory, season=season)

class PurchasePage(MethodView):
    def get(self):
        return render_template('pages/purchase.html')

class ManagementPage(MethodView):
    def get(self):
        return render_template('pages/management.html')

class ProfilePage(MethodView):
    def get(self):
        return render_template('pages/profile.html', username="John Doe", user_email="john.doe@example.com")

app.add_url_rule('/', view_func=HomePage.as_view('home'))
app.add_url_rule('/inventory', view_func=InventoryPage.as_view('inventory'))
app.add_url_rule('/purchase', view_func=PurchasePage.as_view('purchase'))
app.add_url_rule('/management', view_func=ManagementPage.as_view('management'))
app.add_url_rule('/profile', view_func=ProfilePage.as_view('profile'))

if __name__ == '__main__':
    app.run(debug=True)