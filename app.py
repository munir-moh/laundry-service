from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.permanent_session_lifetime = timedelta(hours=1)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)               # Add this
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.', 'error')
        else:
            user = User(name=name, email=email, password=hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('Logged in successfully.', 'success')
            return redirect(url_for('order'))
        else:
            flash('Invalid credentials.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user_id' not in session:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        session['pending_order'] = {
            'name': request.form['name'],
            'phone': request.form['phone'],
            'email': request.form['email'],
            'address': request.form['address'],
            'service': request.form['service'],
            'pickup_date': request.form['pickup_date'],
            'notes': request.form['notes'],
            'order_date': datetime.now().strftime("%A, %d %B %Y"),
            'created_at': datetime.now().timestamp()
        }
        return render_template('confirm_order.html')
    return render_template('order.html')

@app.route('/finalize-order', methods=['POST'])
def finalize_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    pending = session.pop('pending_order', None)
    if pending and datetime.now().timestamp() - pending['created_at'] <= 60:
        order = Order(
            user_id=session['user_id'],
            name=pending['name'],
            phone=pending['phone'],
            email=pending['email'],
            address=pending['address'],
            service=pending['service'],
            pickup_date=pending['pickup_date'],
            notes=pending['notes'],
            order_date=pending['order_date']
        )
        db.session.add(order)
        db.session.commit()
        flash('Order placed successfully.', 'success')
    else:
        flash('Order not finalized (expired or invalid).', 'error')
    return render_template('confirm_order.html', redirect=True)

@app.route('/cancel-order', methods=['POST'])
def cancel_order():
    session.pop('pending_order', None)
    flash('Order cancelled.', 'error')
    return render_template('confirm_order.html', redirect=True)

@app.route('/my-orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))

    orders = Order.query.filter_by(user_id=user.id).all()
    return render_template('my_orders.html', orders=orders)

# Admin section remains unchanged
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == 'munirmuhd12':
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin password.', 'error')
    return render_template('admin_login.html')

@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        order = Order.query.get(request.form.get('order_id'))
        if order:
            order.sorted_status = "Yes"
            db.session.commit()
    orders = Order.query.filter_by(cancelled=False).all()
    return render_template('admin_dashboard.html', orders=orders)

@app.route('/admin/registered_users')
def view_users():
    if not session.get('is_admin'):  # Adjust as per your logic
        return redirect(url_for('login'))

    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin-logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

if __name__ == '__main__':
    app.run(debug=True)
