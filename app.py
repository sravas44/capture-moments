from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import itertools

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ---------- In‑Memory Stores ---------- #
users = {}                      # {username: {id, email, password}}
user_id_counter = itertools.count(1)

bookings = []                   # list of dicts
booking_id_counter = itertools.count(1)

# ---------- Static Photographer Data ---------- #
photographers = [
    {"id": "p1", "name": "Amit Lensman", "skills": ["Wedding", "Portrait"], "image": "amit.jpg", "rating": 4.5, "price": "₹3000"},
    {"id": "p2", "name": "Sana Clickz", "skills": ["Fashion", "Event"], "image": "sana.jpg", "rating": 4.8, "price": "₹3500"},
    {"id": "p3", "name": "Raj Snapper", "skills": ["Event", "Candid"], "image": "raj.jpg", "rating": 4.3, "price": "₹2800"},
    {"id": "p4", "name": "Meena Photos", "skills": ["Baby", "Portrait"], "image": "meena.jpg", "rating": 4.6, "price": "₹3200"},
    {"id": "p5", "name": "Kiran Frames", "skills": ["Wedding", "Fashion"], "image": "kiran.jpg", "rating": 4.7, "price": "₹4000"},
    {"id": "p6", "name": "Latha Studio", "skills": ["Fashion", "Event"], "image": "latha.jpg", "rating": 4.2, "price": "₹2900"},
    {"id": "p7", "name": "Ravi Pixels", "skills": ["Candid", "Portrait"], "image": "ravi.jpg", "rating": 4.4, "price": "₹3100"},
    {"id": "p8", "name": "Divya Capture", "skills": ["Wedding", "Baby"], "image": "divya.jpg", "rating": 4.9, "price": "₹4500"}
]

availability_data = {
    "p1": ["2025-06-20", "2025-06-23"],
    "p2": ["2025-06-19", "2025-06-22"],
    "p3": ["2025-06-25"],
    "p4": ["2025-06-24"],
    "p5": ["2025-06-26"],
    "p6": ["2025-06-22", "2025-06-27"],
    "p7": ["2025-06-20"],
    "p8": ["2025-06-21", "2025-06-28"]
}

# ---------- Routes ---------- #
@app.route('/')
def index():
    return redirect(url_for('home')) if 'user_id' in session else redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        booking = {
            "id": next(booking_id_counter),
            "user_id": session['user_id'],
            "photographer_id": request.form['photographer_id'],
            "date": request.form['date'],
            "price": request.form['price'],
            "address": request.form['address']
        }
        bookings.append(booking)
        flash("Booking successful!", "success")
        return redirect(url_for('orders'))

    return render_template('book.html')

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_bookings = [b for b in bookings if b['user_id'] == session['user_id']]
    return render_template('order.html', bookings=user_bookings)

@app.route('/show-photographers')
def show_photographers():
    return render_template('photographers.html',
                           photographers=photographers,
                           availability_data=availability_data)

@app.route('/wedding')   # …likewise for the rest
def wedding():
    return render_template('wedding.html')

@app.route('/fashion')
def fashion():
    return render_template('fashion.html')

@app.route('/event')
def event():
    return render_template('event.html')

@app.route('/baby')
def baby():
    return render_template('baby.html')

# ---------- Auth ---------- #
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip().lower()
        password = request.form['password']

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))
        if username in users or any(u['email'] == email for u in users.values()):
            flash("Username or email already exists.", "error")
            return redirect(url_for('register'))

        users[username] = {
            "id": next(user_id_counter),
            "email": email,
            "password": generate_password_hash(password)
        }
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username'].strip()
        password = request.form['password']

        # Find user by username OR email
        user = (users.get(username_or_email) or
                next((u for u in users.values() if u['email'] == username_or_email), None))

        if user and check_password_hash(user['password'], password):
            session['user_id']  = user['id']
            session['username'] = next(k for k, v in users.items() if v['id'] == user['id'])
            flash("Logged in successfully.", "success")
            return redirect(url_for('home'))

        flash("Invalid credentials.", "error")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('aboutus.html')

# ---------- Start Server ---------- #
if __name__ == '__main__':
    app.run(debug=True)
