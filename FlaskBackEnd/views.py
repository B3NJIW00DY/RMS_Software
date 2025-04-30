from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from FlaskBackEnd import app

import json

app.secret_key = 'your_secret_key_here'

# ----- STAFF LOGIN SYSTEM -----
valid_staff = {
    "staff1": "letmein"
}

valid_kitchen_staff = {
    "staff2": "hello"
}

valid_manager = {
    "admin": "password123"
}

# ---------- ROUTES ----------

# Home Page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    return render_template('home_page.html', title="Home Page")

# Book Now logic to check login status
@app.route('/book_now')
def book_now():
    if 'customer_logged_in' in session:
        return redirect(url_for('reservation_page'))
    else:
        return redirect(url_for('customer_login'))

# Reservation Page
@app.route('/reservation_page', methods=['GET', 'POST'])
def reservation_page():
    return render_template('reservation.html', title="Make a Reservation")

# Reservation Login Page
@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    return render_template('customer_login.html', title="Customer Login")

# Customer Login Page
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        # Dummy login logic for demonstration
        username = request.form.get('username')
        password = request.form.get('password')

        # Replace this with actual user validation
        if username == 'customer' and password == 'password':
            session['customer_logged_in'] = True
            return redirect(url_for('reservation_page'))
        else:
            flash("Invalid credentials. Please try again.")
            return redirect(url_for('customer_login'))

    return render_template('customer_login_page2.html', title="Customer Login Page 2")

# Staff login page
@app.route('/staff-login', methods=['GET', 'POST'])
def staff_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in valid_staff and valid_staff[username] == password:
            return render_template('Order_Interface.html', username=username)
        elif username in valid_kitchen_staff and valid_kitchen_staff[username] == password:
            return redirect(url_for('order_request'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('staff_login'))

    return render_template('Staff_Login_Page.html', title="Staff Login")

# Manager login page
@app.route('/manager-login', methods=['GET', 'POST'])
def manager_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in valid_manager and valid_manager[username] == password:
            return render_template('login_page.html', username=username)
        else:
            flash("Invalid username or password")
            return redirect(url_for('manager_login'))

    return render_template('Manager_Login_Page.html', title="Manager Login")

# ---------- ORDER SYSTEM ----------

class MenuItem:
    def __init__(self, name, price, is_drink=False):
        self.name = name
        self.price = price
        self.is_drink = is_drink

menu = {
    "Garlic Bread": MenuItem("Garlic Bread", 3.0),
    "Soup": MenuItem("Soup", 4.0),
    "Bruschetta": MenuItem("Bruschetta", 4.5),
    "Burger": MenuItem("Burger", 8.0),
    "Pizza": MenuItem("Pizza", 9.5),
    "Steak": MenuItem("Steak", 15.0),
    "Ice Cream": MenuItem("Ice Cream", 3.5),
    "Cake": MenuItem("Cake", 4.0),
    "Brownie": MenuItem("Brownie", 4.5),
    "Coke": MenuItem("Coke", 2.0, is_drink=True),
    "Lemonade": MenuItem("Lemonade", 2.5, is_drink=True),
    "Water": MenuItem("Water", 1.5, is_drink=True),
}

class OrderItem:
    def __init__(self, name, quantity, status="preparing"):
        self.name = name
        self.quantity = quantity
        self.status = status

class Order:
    def __init__(self, table_number):
        self.table_number = table_number
        self.items = []

    def add_item(self, name, quantity, status="preparing"):
        if name in menu:
            self.items.append(OrderItem(name, quantity, status))

    def calculate_total(self):
        return sum(menu[item.name].price * item.quantity for item in self.items)

    def get_food_items(self):
        return [item for item in self.items if not menu[item.name].is_drink]

    def to_dict(self):
        return {
            "table_number": self.table_number,
            "items": [{"name": item.name, "quantity": item.quantity, "status": item.status} for item in self.items]
        }

    @staticmethod
    def from_dict(data):
        order = Order(data["table_number"])
        for item_data in data["items"]:
            order.add_item(item_data["name"], item_data["quantity"], item_data["status"])
        return order

orders = []

def save_orders():
    with open('orders.json', 'w') as f:
        json.dump([order.to_dict() for order in orders], f, indent=4)

def load_orders():
    global orders
    try:
        with open('orders.json', 'r') as f:
            orders_data = json.load(f)
            orders = [Order.from_dict(order) for order in orders_data]
    except FileNotFoundError:
        orders = []

# Load orders on startup
load_orders()

# Order Interface
@app.route('/order')
def order_page():
    return render_template('Order_Interface.html')

# Submit an order
@app.route('/submit_order', methods=['POST'])
def submit_order():
    table_number = request.form.get('table')
    order_data = request.form.getlist('items[]')

    order = Order(table_number)
    for item in order_data:
        if ':' in item:
            name, quantity = item.split(':')
            order.add_item(name, int(quantity))

    orders.append(order)
    save_orders()

    return redirect(url_for('order_request'))

# View current orders
@app.route('/order-request')
def order_request():
    return render_template('Order_Request.html', orders=orders, menu=menu)

# Update item status
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    table_number = data.get('table_number')
    item_name = data.get('item_name')
    new_status = data.get('new_status')

    for order in orders:
        if order.table_number == table_number:
            for item in order.items:
                if item.name == item_name:
                    item.status = new_status
                    save_orders()
                    return jsonify({"message": "Status updated successfully"}), 200

    return jsonify({"error": "Order or item not found"}), 404
