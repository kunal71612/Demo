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

TREATMENTS = {
    'teeth-cleaning': {
        'title': 'Teeth Cleaning (Scaling)',
        'subtitle': 'Ultrasonic scaling & polishing for pristine oral health',
        'icon': 'scan',
        'image': 'https://images.unsplash.com/photo-1518152006812-edab29b069ac?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'Regular teeth cleaning, or dental scaling, is essential for maintaining healthy gums and teeth. Over time, plaque and tartar build up on your teeth, which can lead to gum disease and cavities if not removed. Our clinical experts use advanced ultrasonic scaling devices to gently and effectively clear plaque, followed by a polishing treatment that leaves your teeth smooth and clean.',
        'benefits': [
            'Removes stubborn plaque and tartar buildup',
            'Prevents gum disease (gingivitis and periodontitis)',
            'Brightens your smile and freshens breath instantly',
            'Helps in early detection of potential dental issues'
        ],
        'procedure': [
            'Physical Exam: The dental hygienist checks your teeth and gums for signs of irritation or issues.',
            'Ultrasonic Scaling: Advanced sonic vibrations are used to remove plaque and tartar from tooth surfaces and below the gumline.',
            'Polishing: A high-powered electric brush and gritty toothpaste are used to remove stains and smooth the enamel.',
            'Flossing & Fluoride: Deep flossing followed by an optional protective fluoride treatment to strengthen your teeth.'
        ]
    },
    'dental-implants': {
        'title': 'Dental Implants',
        'subtitle': 'Permanent, natural-looking tooth restoration solutions',
        'icon': 'bolt',
        'image': 'https://images.unsplash.com/photo-1606811841689-23dfddce3e95?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'Dental implants are the gold standard for replacing missing teeth. They are designed to replicate the natural root structure of a tooth, providing unmatched stability and longevity. A biocompatible titanium post is surgically placed into the jawbone, which fuses with the bone over time to support a custom-crafted crown that looks, feels, and functions just like a natural tooth.',
        'benefits': [
            'Restores full chewing capacity and clear speech',
            'Prevents jawbone loss and maintains facial structure',
            'Saves adjacent teeth from needing down-sizing or modification',
            'Provides a permanent, lifetime solution with proper care'
        ],
        'procedure': [
            'Initial Assessment: Comprehensive 3D scans and clinical exams to plan implant placement.',
            'Implant Placement: Precise surgical insertion of the biocompatible titanium post into the jawbone.',
            'Osseointegration: A healing period of 3-6 months for the bone to securely fuse with the implant.',
            'Abutment & Crown: Attachment of the custom-made porcelain crown to restore your natural smile.'
        ]
    },
    'root-canal': {
        'title': 'Root Canal Treatment',
        'subtitle': 'Painless endodontic therapy to save your natural teeth',
        'icon': 'heart-pulse',
        'image': 'https://images.unsplash.com/photo-1609840114035-3c981b782dfe?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'A root canal is a highly effective, virtually painless procedure designed to save a tooth that is severely decayed or infected. The treatment involves removing the damaged or infected pulp inside the tooth, cleaning and disinfecting the root canals, and then sealing them to prevent future infection. Saving your natural tooth preserves your bite alignment and chewing strength.',
        'benefits': [
            'Eliminates persistent, severe toothaches and sensitivity',
            'Saves the natural tooth from extraction',
            'Prevents the spread of infection to surrounding tissues and jawbone',
            'Restores normal biting pressure and chewing sensation'
        ],
        'procedure': [
            'Local Anesthesia: We ensure the treatment area is completely numb for a pain-free experience.',
            'Pulp Removal: A tiny opening is made in the tooth to access and remove the infected pulp.',
            'Cleaning & Shaping: The inner canals are thoroughly cleaned, disinfected, and shaped.',
            'Sealing: The canals are filled with a biocompatible material (gutta-percha) and sealed, followed by a crown recommendation.'
        ]
    },
    'teeth-whitening': {
        'title': 'Teeth Whitening',
        'subtitle': 'Safe, professional bleaching for a brilliant smile',
        'icon': 'sun-medium',
        'image': 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'Professional teeth whitening is one of the quickest and most impactful ways to transform your smile. Stains from coffee, tea, wine, smoking, or natural aging can dull your teeth over time. Our clinic offers safe, clinical-grade bleaching treatments that break down stains below the enamel surface, brightening your teeth by up to 8 shades in just a single office visit.',
        'benefits': [
            'Fast and dramatic results in under an hour',
            'Safely formulated products that protect enamel and reduce sensitivity',
            'Uniform whitening compared to over-the-counter kits',
            'Boosts confidence and leaves a stunning first impression'
        ],
        'procedure': [
            'Preparation: A protective gel or rubber shield is placed over your gums to keep them safe.',
            'Whitening Gel Application: A high-concentration bleaching gel is applied to the front of your teeth.',
            'Laser Activation: A specialized blue light or laser is used to activate the whitening gel.',
            'Rinse & Evaluation: The gel is rinsed off, and shade improvements are measured and documented.'
        ]
    },
    'crowns-bridges': {
        'title': 'Crowns & Bridges',
        'subtitle': 'High-quality dental restorations for broken or missing teeth',
        'icon': 'crown',
        'image': 'https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'Crowns and bridges are permanent restorative devices used to repair damaged or missing teeth. A dental crown acts as a protective cap that fits entirely over a weakened or broken tooth, restoring its strength, shape, and size. A dental bridge, on the other hand, is used to fill the space left by one or more missing teeth, anchored securely to the surrounding healthy teeth.',
        'benefits': [
            'Strengthens fractured, weak, or heavily filled teeth',
            'Restores natural appearance, shape, and alignment',
            'Bridges gaps to prevent remaining teeth from shifting',
            'Extremely durable restorations lasting 10-15 years'
        ],
        'procedure': [
            'Tooth Preparation: The tooth is reshaped to accommodate the thickness of the crown.',
            'Impression: A digital scan or physical mold is taken to create a custom-fit restoration.',
            'Temporary Crown: A temporary cap is fitted to protect the tooth while the final one is made.',
            'Bonding: The custom-crafted porcelain crown or bridge is permanently cemented in place.'
        ]
    },
    'surgical-extractions': {
        'title': 'Surgical Extractions',
        'subtitle': 'Safe and comfortable removal of impacted or damaged teeth',
        'icon': 'syringe',
        'image': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'description': 'While we always aim to save your natural teeth, there are times when an extraction is the best option for your overall oral health. A surgical extraction is typically required for teeth that cannot be easily accessed, such as impacted wisdom teeth or teeth broken below the gumline. Our team ensures the procedure is carried out with extreme care, absolute sterile safety, and maximum comfort.',
        'benefits': [
            'Prevents overcrowding and shifting of healthy teeth',
            'Relieves intense pain caused by impacted wisdom teeth',
            'Eliminates severe infections that cannot be resolved with root canals',
            'Ensures oral cavity health is protected and stabilized'
        ],
        'procedure': [
            'X-Ray Assessment: Detailed imaging to map the tooth root shape and adjacent structures.',
            'Anesthesia: Administration of local anesthesia (or sedation) for a comfortable procedure.',
            'Gentle Removal: A small incision in the gum is made if needed to safely lift and remove the tooth.',
            'Suturing & Recovery: The socket is cleaned, sterile gauze is placed, and self-dissolving sutures are applied.'
        ]
    }
}

@app.route('/treatment/<slug>')
def treatment_detail(slug):
    """
    Renders the detailed treatment information page based on the dynamic slug.
    If the treatment doesn't exist, redirects back to the index page.
    """
    treatment = TREATMENTS.get(slug)
    if not treatment:
        return redirect(url_for('index'))
    return render_template('treatment_detail.html', treatment=treatment, slug=slug)

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
