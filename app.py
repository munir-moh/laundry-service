from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        service = request.form.get('service')
        pickup_date = request.form.get('pickup_date')
        notes = request.form.get('notes')
        order_date = datetime.now().strftime("%A, %d %B %Y")
        sorted_status = "No"

        with open('orders.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([name, phone, email, address, service, pickup_date, notes, order_date, sorted_status])

        flash('Order placed successfully!')
        return redirect(url_for('order'))

    return render_template('order.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'munirmuhd12':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid password')
    return render_template('admin_login.html')

@app.route('/admin-dashboard', methods=['GET'])
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

    # Check if admin clicked 'Mark as Sorted'
    sort_index = request.args.get('sort')
    if sort_index is not None:
        index = int(sort_index)
        if 0 <= index < len(orders):
            orders[index][-1] = "Yes"
            with open('orders.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(orders)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', orders=orders)

@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
