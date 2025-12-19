from flask import Flask, render_template, request, redirect
import sqlite3
import stripe
import os
from markupsafe import escape

app = Flask(__name__)

# Stripe secret key from Render environment variable
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

def get_db():
    return sqlite3.connect("credit_repair.db")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/consultation", methods=["POST"])
def consultation():
    name = escape(request.form["name"])
    email = escape(request.form["email"])
    phone = escape(request.form["phone"])
    message = escape(request.form["message"])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clients (full_name, email, phone, message)
        VALUES (?, ?, ?, ?)
    """, (name, email, phone, message))

    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": "Credit Repair Service"},
                "unit_amount": 9999,  # $99.99
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://TON-SITE.onrender.com/success",
        cancel_url="https://TON-SITE.onrender.com/",
    )
    return redirect(session.url, code=303)

@app.route("/success")
def success():
    return "<h1>Payment Successful! Thank you.</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
