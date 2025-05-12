import json
import uuid, atexit
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from FlaskBackEnd import app

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

valid_customer = {
    "customer1": "password"
}

# ---------- ROUTES ----------

# Home Page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    return render_template('home_page.html', title="Home Page")

# Reservation Page
@app.route('/reservation_page', methods=['GET', 'POST'])
def reservation_page():
    customer_name = session.get('customer_name', '')
    customer_email = session.get('customer_email', '')
    return render_template(
        'reservation.html',
        title="Make a Reservation",
        customer_name=customer_name,
        customer_email=customer_email
    )

# Reservation Login Page
@app.route('/reservation', methods=['GET', 'POST'])
def reservation():
    return render_template('customer_login.html', title="Customer Login")

@app.route('/view_reservations')
def view_reservations():
    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
    except FileNotFoundError:
        reservations = []

    return render_template('View_reservations.html', reservations=reservations, title="View Reservations")

# Customer Login Page
@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in valid_customer and valid_customer[username] == password:
            session['customer_logged_in'] = True
            session['customer_name'] = 'John Doe'  # Example
            session['customer_email'] = 'john@example.com'  # Example
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
            return render_template('Staff_schedule.html', username=username)
        else:
            flash("Invalid username or password")
            return redirect(url_for('manager_login'))

    return render_template('Manager_Login_Page.html', title="Manager Login")

@app.route('/inventory')
def inventory():
    return render_template('Inventory.html')  

# ----- RESERVATION SYSTEM -----

# Reservation class
class Reservation:
    def __init__(self, name, email, date, time, people, reservation_id=None):
        self.id = reservation_id or str(uuid.uuid4())
        self.name = name
        self.email = email
        self.date = date
        self.time = time
        self.people = people

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "date": self.date,
            "time": self.time,
            "people": self.people
        }

    @staticmethod
    def from_dict(data):
        return Reservation(
            name=data["name"],
            email=data["email"],
            date=data["date"],
            time=data["time"],
            people=data["people"],
            reservation_id=data.get("id")
        )

# Helper function to save reservations to the JSON file
def save_reservations(reservations):
    with open('reservations.json', 'w') as f:
        json.dump([r.to_dict() for r in reservations], f, indent=4)

@app.route('/submit_reservation', methods=['POST'])
def submit_reservation():
    name = request.form.get('name')
    email = request.form.get('email')
    date = request.form.get('date')
    time = request.form.get('time')
    people = request.form.get('people')

    new_reservation = Reservation(name, email, date, time, people)

    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
            reservations = [Reservation.from_dict(r) for r in reservations]
    except FileNotFoundError:
        reservations = []

    reservations.append(new_reservation)
    save_reservations(reservations)

    flash(f"Reservation made for {name}")
    return redirect(url_for('home'))

@app.route('/amend_reservation/<reservation_id>', methods=['GET', 'POST'])
def amend_reservation(reservation_id):
    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
            reservations = [Reservation.from_dict(r) for r in reservations]
    except FileNotFoundError:
        reservations = []

    reservation_to_amend = next((r for r in reservations if r.id == reservation_id), None)

    if not reservation_to_amend:
        flash("Reservation not found.")
        return redirect(url_for('view_reservations'))

    if request.method == 'POST':
        reservation_to_amend.name = request.form.get('name')
        reservation_to_amend.email = request.form.get('email')
        reservation_to_amend.date = request.form.get('date')
        reservation_to_amend.time = request.form.get('time')
        reservation_to_amend.people = request.form.get('people')

        save_reservations(reservations)

        flash(f"Reservation for {reservation_to_amend.name} updated successfully.")
        return redirect(url_for('view_reservations'))

    return render_template('Reservation.html', reservation=reservation_to_amend)

@app.route('/cancel_reservation/<reservation_id>', methods=['POST'])
def cancel_reservation(reservation_id):
    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
            reservations = [Reservation.from_dict(r) for r in reservations]
    except FileNotFoundError:
        reservations = []

    reservations = [r for r in reservations if r.id != reservation_id]

    save_reservations(reservations)

    flash("Reservation has been canceled.")
    return redirect(url_for('view_reservations'))

# ----- ORDER SYSTEM -----

# Menu and Order Management Classes
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
        json.dump([order.to_dict() for order in orders], f)

@app.route('/order_request')
def order_request():
    return render_template('Order_Request.html', title="Order Request")

@app.route('/submit_order', methods=['POST'])
def submit_order():
    table_number = request.form.get('table_number')
    order = Order(table_number)

    for item_name in request.form.getlist('items'):
        quantity = int(request.form.get(f'{item_name}_quantity'))
        order.add_item(item_name, quantity)

    orders.append(order)
    save_orders()

    flash(f"Order for table {table_number} has been placed.")
    return redirect(url_for('view_orders'))

@app.route('/view_orders')
def view_orders():
    try:
        with open('orders.json', 'r') as f:
            order_data = json.load(f)
            loaded_orders = [Order.from_dict(o) for o in order_data]
    except FileNotFoundError:
        loaded_orders = []

    print(loaded_orders)  # To see what data is being passed to the template

    return render_template('Order_Request.html', orders=loaded_orders, title="View Orders")


@app.route('/order')
def order_page():
    return render_template('Order_Interface.html', orders=orders)

@app.route('/complete_order/<order_id>', methods=['POST'])
def complete_order(order_id):
    global orders
    orders = [order for order in orders if order.table_number != order_id]

    # Save the updated orders list to the JSON file
    save_orders()

    flash(f"Order for table {order_id} has been completed.")
    return redirect(url_for('view_orders'))

@app.route('/staff_schedule')
def staff_schedule():
    return render_template('Staff_Schedule.html', title="Staff Schedule")


if __name__ == '__main__':
    app.run(debug=True)
