from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with your secret key

# Home/Dashboard
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Services
@app.route('/services')
def services():
    return render_template('services.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Contact
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Order Page
@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        service = request.form.get('service')
        pickup_date = request.form.get('pickup_date')
        notes = request.form.get('notes')

        with open('orders.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, address, service, pickup_date, notes])

        flash('Order placed successfully!')
        return redirect(url_for('order'))

    return render_template('order.html')

# Admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'munirmuhd12':  # Replace with your own password
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password')
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    orders = []
    if os.path.exists('orders.csv'):
        with open('orders.csv', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:
                    orders.append(row)

    return render_template('admin_dashboard.html', orders=orders)

@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('dashboard'))

if __name__ == '_main_':
    app.run(debug=True)