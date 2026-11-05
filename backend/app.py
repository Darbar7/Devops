import os
from flask import Flask
import psycopg2
import redis

app = Flask(__name__)

# Read configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

@app.route("/")
def home():
    try:
        # Test PostgreSQL connection
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        conn.close()
        db_status = "Connected to PostgreSQL successfully!"
    except Exception as e:
        db_status = f"PostgreSQL Connection Error: {e}"

    try:
        # Test Redis connection
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_timeout=2)
        r.ping()
        redis_status = "Connected to Redis successfully!"
    except Exception as e:
        redis_status = f"Redis Connection Error: {e}"

    return f"<h1>DevOps E-Commerce Backend</h1><p>{db_status}</p><p>{redis_status}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)