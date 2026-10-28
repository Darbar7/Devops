from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the E-Commerce DevOps API!"})

@app.route('/products', methods=['GET'])
def get_products():
    products = [
        {"id": 1, "name": "Mechanical Keyboard", "price": 49.99},
        {"id": 2, "name": "Wireless Mouse", "price": 29.99},
        {"id": 3, "name": "USB-C Hub", "price": 19.99}
    ]
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)