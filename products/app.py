from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

products_cache = []

def fetch_products():
    try:
        response = requests.get('https://dummyjson.com/products')
        response.raise_for_status()
        data = response.json()
        return data.get('products', [])

    except requests.RequestException as e:
        print(f"Error in fetching products: {e}")
        return None

@app.route('/products', methods=['GET'])
def get_products():
    global products_cache
    if not products_cache:
        products_cache = fetch_products()
        if products_cache is None:
            return jsonify({"error": "Failed to fetch products from external API"}), 503
    return jsonify(products_cache), 200

@app.route('/products', methods=['POST'])
def add_product():
    global products_cache

    data = request.json
    required_fields = ['title', 'price', 'category']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({
            "error": "Missing fields in request",
            "missing_fields": missing_fields
        }), 400

    optional_fields = {
        "availabilityStatus": "In Stock",
        "brand": None,
        "description": None,
        "dimensions": {"depth": 0.0, "height": 0.0, "width": 0.0},
        "discountPercentage": 0.0,
        "images": [],
        "meta": {
            "barcode": None,
            "createdAt": None,
            "qrCode": None,
            "updatedAt": None
        },
        "minimumOrderQuantity": 1,
        "rating": 0.0,
        "returnPolicy": "No return policy",
    }

    product_data = {key: data.get(key, default) for key, default in optional_fields.items()}
    product_data.update({
        "id": len(products_cache) + 1,
        "title": data['title'],
        "price": data['price'],
        "category": data['category']
    })

    products_cache.append(product_data)
    return jsonify(product_data), 201

if __name__ == '__main__':
    app.run(debug=True)