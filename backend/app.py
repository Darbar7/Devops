import os
import redis
import psycopg2
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'

# Environment variables from Docker Compose
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('DB_NAME', 'ecommerce')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'secretpassword')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_redis_connection():
    return redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Initialize Database Tables on Startup
with get_db_connection() as conn:
    with conn.cursor() as cur:
        # Products table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            );
        ''')
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
            );
        ''')
        # Orders table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                items JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()

# --- Frontend Routes ---
@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products;")
    rows = cur.fetchall()
    products = [{"id": row[0], "name": row[1], "price": float(row[2])} for row in rows]
    cur.close()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/health')
def health_check():
    health_status = {"backend": "healthy", "database": "disconnected", "redis": "disconnected"}
    try:
        conn = get_db_connection()
        conn.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = str(e)

    try:
        r = get_redis_connection()
        r.ping()
        health_status["redis"] = "connected"
    except Exception as e:
        health_status["redis"] = str(e)

    return jsonify(health_status)

# --- Auth Endpoints ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id;", (username, hashed_password))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": user_id, "message": "User registered successfully!"}), 201
    except Exception as e:
        return jsonify({"error": "Username already exists or database error"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        token = jwt.encode({
            'user_id': user[0],
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token, "message": "Login successful!"})

    return jsonify({"error": "Invalid username or password"}), 401

# --- Products & Cart API ---
@app.route('/api/products', methods=['GET', 'POST'])
def manage_products():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        price = data.get('price')
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id;", (name, price))
        product_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": product_id, "message": "Product added successfully!"}), 201

    cur.execute("SELECT id, name, price FROM products;")
    rows = cur.fetchall()
    products = [{"id": row[0], "name": row[1], "price": float(row[2])} for row in rows]
    cur.close()
    conn.close()
    return jsonify(products)

@app.route('/api/cart/<username>', methods=['GET', 'POST'])
def manage_cart(username):
    r = get_redis_connection()
    cart_key = f"cart:{username}"

    if request.method == 'POST':
        data = request.json
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        r.hincrby(cart_key, product_id, quantity)
        return jsonify({"message": "Cart updated successfully!"})

    cart_items = r.hgetall(cart_key)
    return jsonify(cart_items)

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username is required for checkout"}), 400

    r = get_redis_connection()
    cart_key = f"cart:{username}"
    cart_items = r.hgetall(cart_key)

    if not cart_items:
        return jsonify({"error": "Your cart is empty"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    total_amount = 0.0
    processed_items = []

    for product_id, quantity in cart_items.items():
        cur.execute("SELECT name, price FROM products WHERE id = %s;", (product_id,))
        product = cur.fetchone()
        if product:
            name, price = product[0], float(product[1])
            qty = int(quantity)
            item_total = price * qty
            total_amount += item_total
            processed_items.append({"product_id": product_id, "name": name, "price": price, "quantity": qty})

    cur.execute(
        "INSERT INTO orders (username, total_amount, items) VALUES (%s, %s, %s) RETURNING id;",
        (username, total_amount, str(processed_items))
    )
    order_id = cur.fetchone()[0]
    conn.commit()

    r.delete(cart_key)
    cur.close()
    conn.close()

    return jsonify({
        "order_id": order_id,
        "username": username,
        "total_amount": total_amount,
        "items": processed_items,
        "message": "Checkout successful! Order placed."
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)