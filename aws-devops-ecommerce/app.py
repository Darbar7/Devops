import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database connection helper with retry logic for startup
def get_db_connection():
    retries = 10
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host='db',
                database=os.environ.get('DB_NAME', 'todo_db'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'mysecretpassword')
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready. Retrying... ({10 - retries}/10)")
            time.sleep(3)
    raise Exception("Could not connect to the database")

# Initialize database table
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                task TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE
            );
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database table 'todos' initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Automatically initialize database when Gunicorn loads the module
init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, task, completed FROM todos;')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO todos (task) VALUES (%s);', (task,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete(todo_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM todos WHERE id = %s;', (todo_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)