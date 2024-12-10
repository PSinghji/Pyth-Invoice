from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "app/static/logos"

# MySQL connection settings
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "root"),
        database=os.environ.get("MYSQL_DB", "invoice_db")
    )

# Initialize the database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(255) NOT NULL,
            logo_path VARCHAR(255),
            invoice_date DATE NOT NULL,
            total_amount DECIMAL(10, 2) NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def list_invoices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM invoices")
    invoices = cursor.fetchall()
    conn.close()
    return render_template("index.html", invoices=invoices)

@app.route("/create", methods=["GET", "POST"])
def create_invoice():
    if request.method == "POST":
        company_name = request.form.get("company_name")
        logo = request.files.get("logo")
        invoice_date = request.form.get("invoice_date")
        total_amount = request.form.get("total_amount")

        logo_path = None
        if logo and logo.filename:
            logo_path = os.path.join(app.config["UPLOAD_FOLDER"], logo.filename)
            logo.save(logo_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (company_name, logo_path, invoice_date, total_amount)
            VALUES (%s, %s, %s, %s)
        """, (company_name, logo_path, invoice_date, total_amount))
        conn.commit()
        conn.close()

        return redirect(url_for("list_invoices"))
    return render_template("create_invoice.html")

@app.route("/invoice/<int:invoice_id>")
def view_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM invoices WHERE id = %s", (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()
    return render_template("invoice.html", invoice=invoice)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
