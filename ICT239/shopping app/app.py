from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/")
def home():
    return "Hello, Flask!"

items = [
    {
        "item_id": 1,
        "item_name": "Notebook",
        "item_description": "A ruled notebook, perfect for school or work.",
        "inventory_quantity": 10,
        "price": 5.50,
        "image_url": "https://static.platform.michaels.com/2c-prd/en_US/4611909929747519792.jpeg"
    },
    {
        "item_id": 2,
        "item_name": "Pen",
        "item_description": "Blue ink ballpoint pen with smooth writing.",
        "inventory_quantity": 25,
        "price": 2.00,
        "image_url": "https://tiimg.tistatic.com/fp/1/007/680/very-smooth-small-rotating-cello-blue-ball-pen-with-fine-grip-602.jpg"
    },
    {
        "item_id": 3,
        "item_name": "Backpack",
        "item_description": "Durable canvas backpack for everyday use.",
        "inventory_quantity": 5,
        "price": 35.00,
        "image_url": "https://m.media-amazon.com/images/I/813WffuRx+L._UY1000_.jpg"
    },
    {
        "item_id": 4,
        "item_name": "Water Bottle",
        "item_description": "Insulated water bottle keeps drinks cold or hot.",
        "inventory_quantity": 15,
        "price": 12.00,
        "image_url": "https://m.media-amazon.com/images/I/51yGqnrBYqL._UF894,1000_QL80_.jpg"
    },
    {
        "item_id": 5,
        "item_name": "Headphones",
        "item_description": "Over-ear headphones with noise cancellation.",
        "inventory_quantity": 8,
        "price": 60.00,
        "image_url": "https://m.media-amazon.com/images/I/713SMXPRweL._UF894,1000_QL80_.jpg"
    }
]



@app.route("/shop")
def shop():
    return render_template("shop.html", items=items)

# @app.route("/shop/<item_id>")
# def shop_item_id(item_id):
#     return f"Test item: {item_id}"

@app.route("/shop/<int:item_id>", methods=["GET", "POST"])
def shop_item_id(item_id):
    # Find the item
    item = next((i for i in items if i["item_id"] == item_id), None)
    if not item:
        return "Item not found", 404

    if request.method == "POST":
        quantity = int(request.form.get("quantity", 0))
        if quantity > item["inventory_quantity"]:
            quantity = item["inventory_quantity"]

        # Initialize cart in session
        if "cart" not in session:
            session["cart"] = []

        # Check if item already in cart
        cart = session["cart"]
        existing = next((c for c in cart if c["item_id"] == item_id), None)
        if existing:
            existing["quantity"] += quantity
        else:
            cart.append({
                "item_id": item["item_id"],
                "item_name": item["item_name"],
                "price": item.get("price", 10.0),  # assign default price if not set
                "quantity": quantity
            })
        session["cart"] = cart  # save back to session
        return redirect(url_for("shop"))  # stay on shop, just added to cart

    return render_template("item.html", item=item)

@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    final_total = sum(item["quantity"] * item["price"] for item in cart)
    return render_template("cart.html", cart=cart, final_total=final_total)

@app.route("/checkout")
def checkout():
    session.pop("cart", None)  # clear cart after checkout
    return render_template("checkout.html")


if __name__ == "__main__":
    app.run(debug=True)
