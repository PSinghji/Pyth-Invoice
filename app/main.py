from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

# Database file path
DATABASE = "data/database.db"


# Initialize the database
def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            logo_path TEXT,
            invoice_date TEXT NOT NULL,
            total_amount REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create_invoice():
    if request.method == "POST":
        company_name = request.form["company_name"]
        logo = request.files["logo"]
        invoice_date = request.form["invoice_date"]
        total_amount = request.form["total_amount"]

        # Save the logo file
        logo_path = None
        if logo:
            logo_path = os.path.join("static/logos", logo.filename)
            logo.save(logo_path)

        # Insert into the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (company_name, logo_path, invoice_date, total_amount)
            VALUES (?, ?, ?, ?)
        """, (company_name, logo_path, invoice_date, total_amount))
        conn.commit()
        conn.close()

        return redirect(url_for("list_invoices"))
    return render_template("create_invoice.html")


@app.route("/invoices")
def list_invoices():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()
    conn.close()
    return render_template("index.html", invoices=invoices)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0")
