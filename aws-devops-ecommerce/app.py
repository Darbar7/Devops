import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'super_secret_devops_key'  # Needed for sessions and flash messages

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL', 'postgresql://myuser:mypassword@db:5432/mydatabase')
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise Exception("Could not connect to the database")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) DEFAULT 'General',
            price DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            name VARCHAR(100) NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Ensure tables are created on startup using app context
with app.app_context():
    try:
        init_db()
        print("Database tables initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = 'SELECT * FROM products WHERE 1=1'
    params = []
    
    if search:
        query += ' AND name ILIKE %s'
        params.append(f'%{search}%')
    if category and category != 'All':
        query += ' AND category = %s'
        params.append(category)
        
    cur.execute(query, tuple(params))
    products = cur.fetchall()
    
    # Fetch distinct categories for the filter dropdown
    cur.execute('SELECT DISTINCT category FROM products;')
    categories = [row[0] for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    user_name = session.get('user_name', None)
    return render_template('index.html', products=products, categories=categories, user_name=user_name)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "admin@devops.com" and password == "admin123":
            session['user_name'] = "DevOps Admin"
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    return render_template('cart.html', user_name=session.get('user_name'))

@app.route('/profile')
def profile():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('profile.html', user_name=session.get('user_name'))

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)