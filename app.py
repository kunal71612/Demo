"""
SmileCraft Dental Clinic - Web Application
Built with Python Flask & SQLite3.
Designed with a clean, beginner-friendly structure.
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
# Secret key for encrypting session cookies. In production, keep this secure!
app.secret_key = 'smilecraft_secret_key_for_session_management'

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    Configures row factory to return dictionaries for clean data access in templates.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database schema by creating the appointments table if it doesn't exist yet.
    """
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                treatment TEXT NOT NULL,
                preferred_date TEXT NOT NULL,
                preferred_time TEXT NOT NULL,
                message TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Ensure the database and tables are set up right away
init_db()

@app.route('/')
def index():
    """
    Renders the public dental clinic website homepage, including the hero, services,
    feedback, doctor bio, contact info, and booking form.
    """
    return render_template('index.html')

@app.route('/book', methods=['POST'])
def book_appointment():
    """
    Handles appointment booking requests submitted via AJAX (Fetch API).
    Validates form data and inserts it securely into SQLite.
    """
    try:
        # Extract fields from the form request
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        treatment = request.form.get('treatment', '').strip()
        preferred_date = request.form.get('date', '').strip()
        preferred_time = request.form.get('time', '').strip()
        message = request.form.get('message', '').strip()

        # Basic validation
        if not all([name, phone, email, treatment, preferred_date, preferred_time]):
            return jsonify({
                'success': False,
                'message': 'Please fill in all mandatory fields.'
            }), 400

        # Insert booking details into SQLite database
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO appointments (name, phone, email, treatment, preferred_date, preferred_time, message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, treatment, preferred_date, preferred_time, message))
            conn.commit()

        return jsonify({
            'success': True,
            'message': f'Thank you, {name}! Your appointment slot for {preferred_date} at {preferred_time} has been successfully requested. We will contact you shortly!'
        })

    except Exception as e:
        # Return generic server error message
        return jsonify({
            'success': False,
            'message': f'An unexpected database error occurred: {str(e)}'
        }), 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """
    Renders and handles the admin login page.
    Default credentials should be changed by the clinic administrator after deployment.
    """
    # If already logged in, redirect directly to dashboard
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('admin_login.html', error=error)

@app.route('/admin')
def admin_dashboard():
    """
    Administrative Dashboard displaying appointment registrations.
    Includes analytics summary counters, client-side/server-side filters (search and dates).
    """
    # Simple middleware authorization check
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    # Fetch query filters
    search_query = request.args.get('q', '').strip()
    date_filter = request.args.get('date', '').strip()

    conn = get_db_connection()

    # Core Query construction
    query = "SELECT * FROM appointments WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR phone LIKE ? OR email LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'])

    if date_filter:
        query += " AND preferred_date = ?"
        params.append(date_filter)

    # Order newest appointments first
    query += " ORDER BY created_at DESC"

    appointments = conn.execute(query, params).fetchall()

    # Calculate statistics summaries for dashboard widgets
    stats = {
        'total': conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        'pending': conn.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Pending'").fetchone()[0],
        'completed': conn.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Completed'").fetchone()[0]
    }

    conn.close()

    return render_template('admin.html', 
                           appointments=appointments, 
                           stats=stats, 
                           search_query=search_query, 
                           date_filter=date_filter)

@app.route('/admin/complete/<int:appointment_id>', methods=['POST'])
def mark_completed(appointment_id):
    """
    Marks an appointment status as 'Completed'.
    """
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    with get_db_connection() as conn:
        conn.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?", (appointment_id,))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    """
    Removes an appointment row completely from SQLite.
    """
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    with get_db_connection() as conn:
        conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    """
    Logs out the administrative operator by clearing user session tokens.
    """
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    # Running standard dev port as per instructions
    app.run(debug=True, host='127.0.0.1', port=5000)
