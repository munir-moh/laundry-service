from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import session
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.String(200))
    service = db.Column(db.String(100))
    pickup_date = db.Column(db.String(50))
    notes = db.Column(db.Text)
    order_date = db.Column(db.String(100))
    sorted_status = db.Column(db.String(10), default="No")
    cancelled = db.Column(db.Boolean, default=False)
    cancel_reason = db.Column(db.Text)

# Create database tables
with app.app_context():
    db.create_all()

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
        new_order = Order(
            name = request.form.get('name'),
            phone = request.form.get('phone'),
            email = request.form.get('email'),
            address = request.form.get('address'),
            service = request.form.get('service'),
            pickup_date = request.form.get('pickup_date'),
            notes = request.form.get('notes'),
            order_date = datetime.now().strftime("%A, %d %B %Y"),
            sorted_status = "No"
        )
        db.session.add(new_order)
        db.session.commit()
        return render_template('confirm_order.html', order_id=new_order.id)
    return render_template('order.html')

@app.route('/finalize-order', methods=['POST'])
def finalize_order():
    pending = session.pop('pending_order', None)
    if pending:
        new_order = Order(
            name=pending['name'],
            phone=pending['phone'],
            email=pending['email'],
            address=pending['address'],
            service=pending['service'],
            pickup_date=pending['pickup_date'],
            notes=pending['notes'],
            order_date=pending['order_date'],
            sorted_status="No"
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Order placed successfully!')
    return redirect(url_for('order'))

@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    pending = session.pop('pending_order', None)
    reason = request.form.get('cancel_reason')
    if pending:
        cancelled_order = Order(
            name=pending['name'],
            phone=pending['phone'],
            email=pending['email'],
            address=pending['address'],
            service=pending['service'],
            pickup_date=pending['pickup_date'],
            notes=pending['notes'],
            order_date=pending['order_date'],
            sorted_status="Cancelled",
            cancelled=True,
            cancel_reason=reason
        )
        db.session.add(cancelled_order)
        db.session.commit()
        flash('Order was cancelled within the 1-minute window.')
    return redirect(url_for('order'))

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

@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        order_id = request.form.get('order_id')
        order = Order.query.get(order_id)
        if order:
            order.sorted_status = "Yes"
            db.session.commit()
        return redirect(url_for('admin_dashboard'))

    orders = Order.query.all()
    return render_template('admin_dashboard.html', orders=orders)

@app.route('/mark-sorted/<int:order_id>')
def mark_sorted(order_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    order = Order.query.get(order_id)
    if order:
        order.sorted_status = "Yes"
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)
