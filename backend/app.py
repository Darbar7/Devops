from flask import Flask
import os
import redis
import psycopg2

app = Flask(__name__)

# Environment variables for database and redis connections
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_NAME = os.environ.get('DB_NAME', 'ecommerce')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

@app.route('/')
def home():
    return "Welcome to the E-Commerce DevOps Application!"

@app.route('/health')
def health():
    try:
        # Test Database Connection
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.close()
        
        # Test Redis Connection
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=2)
        r.ping()
        
        return {"status": "healthy", "database": "connected", "redis": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)