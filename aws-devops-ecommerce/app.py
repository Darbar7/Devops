import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
    # Create products table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL
        );
    ''')
    # Create orders table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_email VARCHAR(100) NOT NULL,
            total DECIMAL(10, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Initialize tables on startup
try:
    init_db()
except Exception as e:
    print(f"Skipping init_db on startup: {e}")

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)