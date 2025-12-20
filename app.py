from flask import Flask, render_template, request, redirect, flash
import sqlite3
import stripe
import os
from markupsafe import escape

app = Flask(__name__)

# Clé secrète pour activer les flash messages
app.secret_key = "une_cle_secrete_pour_flash"  # Change-la pour plus de sécurité

# Stripe secret key depuis variable d'environnement Render
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Connexion à la base SQLite
def get_db():
    return sqlite3.connect("credit_repair.db")

# Page d'accueil
@app.route("/")
def home():
    return render_template("index.html")

# Route pour Free Consultation
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

    # Flash message de confirmation
    flash("✅ Merci ! Votre demande de consultation a été envoyée avec succès.")
    return redirect("/")

# Route pour Stripe Checkout
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

# Page succès paiement
@app.route("/success")
def success():
    return "<h1>Payment Successful! Thank you.</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
