from flask import Flask, render_template, request, redirect, flash
import psycopg2
import stripe
import os
from markupsafe import escape

app = Flask(__name__)
app.secret_key = "your_secret_key"  # nécessaire pour flash messages

# Stripe secret key from Render environment variable
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# PostgreSQL connection
def get_db():
    conn = psycopg2.connect(
        host="dpg-d52sqkv5r7bs73dv7ls0-a.render.com",
        database="credit_repair_db",
        user="credit_repair_db_user",
        password="uj6uFsrJMsVmVNxkUKIbcoliafJtdJuQ",
        port=5432
    )
    return conn

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
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, message))

    conn.commit()
    conn.close()

    flash("✅ Merci ! Votre demande de consultation a été reçue. Nous vous contacterons bientôt.")
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
