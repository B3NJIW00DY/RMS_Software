"""
from flask import render_template
from FlaskBackEnd import app

@app.route('/')
@app.route('/home')
def home():
    Renders the home page.
    return render_template(
        'Staff_Login_Page.html',
        title='Home Page'
    )

@app.route('/order-request')
def order_request():
    return render_template('Order_Request.html')

if __name__ == '__main__':
    app.run(debug=True)
"""