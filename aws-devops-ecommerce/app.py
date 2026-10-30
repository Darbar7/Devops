import os
import time
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Get database URL from environment variable (provided by docker-compose)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:password@db:5432/echecommerce')

def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except psycopg2.OperationalError as e:
            retries -= 1
            print(f"Database not ready. Retrying... ({10 - retries}/10)")
            time.sleep(3)
    raise Exception("Could not connect to the database")

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Example query - ensuring table exists or fetching items
        cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            );
        ''')
        conn.commit()
        
        cur.execute('SELECT * FROM products;')
        products = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', products=products)
    except Exception as e:
        return f"Database connection error: {str(e)}"

@app.route('/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = request.form.get('price')
    if name and price:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO products (name, price) VALUES (%s, %s);', (name, price))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)