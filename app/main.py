from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename
from fpdf import FPDF

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'app/static/logos/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

DATABASE = 'data/database.db'

def init_db():
    """Initialize the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            gst_number TEXT,
            invoice_number TEXT,
            customer_name TEXT,
            customer_address TEXT,
            customer_gst TEXT,
            items TEXT,
            total_amount REAL,
            logo TEXT
        )
    ''')
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if the file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Display the home page."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices')
    invoices = cursor.fetchall()
    conn.close()
    return render_template('index.html', invoices=invoices)

@app.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """Create a new invoice."""
    if request.method == 'POST':
        # Get form data
        company_name = request.form['company_name']
        gst_number = request.form['gst_number']
        invoice_number = request.form['invoice_number']
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        customer_gst = request.form['customer_gst']
        items = request.form['items']
        total_amount = request.form['total_amount']

        # Handle logo upload
        logo_file = request.files['logo']
        if logo_file and allowed_file(logo_file.filename):
            logo_filename = secure_filename(logo_file.filename)
            logo_path = os.path.join(app.config['UPLOAD_FOLDER'], logo_filename)
            logo_file.save(logo_path)
        else:
            logo_path = None

        # Insert into database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO invoices (company_name, gst_number, invoice_number, customer_name, customer_address, customer_gst, items, total_amount, logo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_name, gst_number, invoice_number, customer_name, customer_address, customer_gst, items, total_amount, logo_path))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('create_invoice.html')

@app.route('/invoice/<int:invoice_id>')
def view_invoice(invoice_id):
    """View a specific invoice."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()

    if invoice:
        return render_template('invoice.html', invoice=invoice)
    return "Invoice not found!", 404

@app.route('/download/<int:invoice_id>')
def download_invoice(invoice_id):
    """Generate and download a PDF invoice."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
    invoice = cursor.fetchone()
    conn.close()

    if not invoice:
        return "Invoice not found!", 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, f"Invoice #{invoice[3]}", ln=True, align='C')

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Company Name: {invoice[1]}", ln=True)
    pdf.cell(0, 10, f"GST Number: {invoice[2]}", ln=True)
    pdf.cell(0, 10, f"Customer Name: {invoice[4]}", ln=True)
    pdf.cell(0, 10, f"Customer Address: {invoice[5]}", ln=True)
    pdf.cell(0, 10, f"Customer GST: {invoice[6]}", ln=True)
    pdf.cell(0, 10, f"Items: {invoice[7]}", ln=True)
    pdf.cell(0, 10, f"Total Amount: {invoice[8]} INR", ln=True)

    if invoice[9]:
        pdf.image(invoice[9], x=10, y=80, w=50)  # Add logo if available

    pdf_file = f"Invoice_{invoice[3]}.pdf"
    pdf.output(pdf_file)

    return send_file(pdf_file, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
