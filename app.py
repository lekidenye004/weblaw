# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'nanyuki-law-secret-key-2026'

# Database setup
DATABASE = 'nanyuki_law.db'


def get_db():
    """Connect to the SQLite database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create lawyers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lawyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT NOT NULL,
                speciality TEXT NOT NULL,
                bio TEXT,
                email TEXT,
                phone TEXT,
                image_url TEXT
            )
        ''')

        # Create practice areas table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS practice_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                icon_class TEXT
            )
        ''')

        # Create testimonials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                content TEXT NOT NULL,
                rating INTEGER DEFAULT 5
            )
        ''')

        # Create firm_info table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS firm_info (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Insert sample lawyers if empty
        cursor.execute('SELECT COUNT(*) FROM lawyers')
        if cursor.fetchone()[0] == 0:
            lawyers = [
                ('Jane Wanjiru', 'Senior Advocate', 'Litigation & Property',
                 'Over 15 years of experience in civil litigation and property law.',
                 'jane@nanyukilaw.co.ke', '+254 712 345 678', ''),
                ('David Mwangi', 'Advocate', 'Corporate & Commercial',
                 'Specializing in corporate law, mergers, and commercial transactions.',
                 'david@nanyukilaw.co.ke', '+254 723 456 789', ''),
                ('Grace Akinyi', 'Advocate', 'Family & Succession',
                 'Passionate about family law and succession planning.',
                 'grace@nanyukilaw.co.ke', '+254 734 567 890', ''),
                ('Samuel Kariuki', 'Associate', 'Criminal Defence',
                 'Experienced in criminal law, bail applications, and appeals.',
                 'samuel@nanyukilaw.co.ke', '+254 745 678 901', ''),
                ('Faith N. Kamau', 'Associate', 'Employment & Labour',
                 'Expert in employment law, workplace disputes, and labour relations.',
                 'faith@nanyukilaw.co.ke', '+254 756 789 012', '')
            ]
            cursor.executemany(
                'INSERT INTO lawyers (name, title, speciality, bio, email, phone, image_url) VALUES (?,?,?,?,?,?,?)',
                lawyers
            )

        # Insert practice areas if empty
        cursor.execute('SELECT COUNT(*) FROM practice_areas')
        if cursor.fetchone()[0] == 0:
            areas = [
                ('Corporate & Commercial', 'Company formation, contracts, compliance, and business advisory.',
                 'fa-building'),
                ('Property & Land', 'Conveyancing, leases, land disputes, and property transactions.', 'fa-home'),
                ('Litigation & Dispute', 'Civil and commercial litigation, arbitration, and mediation.', 'fa-gavel'),
                ('Family & Succession', 'Divorce, child custody, succession, and estate planning.', 'fa-user-tie'),
                ('Employment & Labour', 'Employment contracts, workplace disputes, and union matters.', 'fa-briefcase'),
                ('Criminal Defence', 'Expert representation in criminal proceedings, bail applications.',
                 'fa-balance-scale')
            ]
            cursor.executemany(
                'INSERT INTO practice_areas (name, description, icon_class) VALUES (?,?,?)',
                areas
            )

        # Insert testimonials if empty
        cursor.execute('SELECT COUNT(*) FROM testimonials')
        if cursor.fetchone()[0] == 0:
            testimonials = [
                ('Peter Mwangi',
                 'I was impressed by the professionalism and dedication. They handled my land dispute with great care.',
                 5),
                ('Sarah Wanjiru',
                 'Excellent service! The team made the divorce process less stressful and guided me every step.', 5),
                ('John Kimathi',
                 'Great legal advice and representation. They truly understand the local legal landscape.', 4)
            ]
            cursor.executemany(
                'INSERT INTO testimonials (client_name, content, rating) VALUES (?,?,?)',
                testimonials
            )

        # Insert firm info
        cursor.execute('SELECT COUNT(*) FROM firm_info')
        if cursor.fetchone()[0] == 0:
            info = [
                ('firm_name', 'Nanyuki Law Advocates'),
                ('firm_location', 'Nanyuki, Laikipia County'),
                ('years', '12'),
                ('address', 'Kenyatta Street, Nanyuki Town'),
                ('phone', '+254 700 123 456'),
                ('email', 'info@nanyukilaw.co.ke'),
                ('hours', 'Mon-Fri: 8:00am – 5:30pm, Sat: 9:00am – 1:00pm'),
                ('description',
                 'Nanyuki Law Advocates has been serving the local community for over a decade. We are a full-service firm with deep roots in Nanyuki and a reputation for integrity, professionalism, and results.')
            ]
            cursor.executemany(
                'INSERT INTO firm_info (key, value) VALUES (?,?)',
                info
            )

        db.commit()


@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT key, value FROM firm_info')
    firm_info = {row['key']: row['value'] for row in cursor.fetchall()}

    cursor.execute('SELECT * FROM practice_areas LIMIT 3')
    practice_areas = cursor.fetchall()

    cursor.execute('SELECT * FROM testimonials ORDER BY rating DESC')
    testimonials = cursor.fetchall()

    return render_template('index.html',
                           firm_info=firm_info,
                           practice_areas=practice_areas,
                           testimonials=testimonials)


@app.route('/lawyers')
def lawyers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM lawyers')
    lawyers = cursor.fetchall()
    return render_template('index.html', lawyers=lawyers)


@app.route('/services')
def services():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM practice_areas')
    practice_areas = cursor.fetchall()
    return render_template('index.html', practice_areas=practice_areas)


@app.route('/about')
def about():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT key, value FROM firm_info')
    firm_info = {row['key']: row['value'] for row in cursor.fetchall()}
    return render_template('index.html', firm_info=firm_info)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        print(f"New enquiry from {name} ({email}): {message}")
        flash('Thank you for your message! A member of our team will respond within 24 hours.', 'success')
        return redirect(url_for('contact'))

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT key, value FROM firm_info')
    firm_info = {row['key']: row['value'] for row in cursor.fetchall()}
    return render_template('index.html', firm_info=firm_info)


@app.route('/schedule')
def schedule():
    """Redirect to WhatsApp for scheduling"""
    phone = "254700057910"  # Your phone number without the leading 0
    message = "Hello, I would like to schedule a consultation with Nanyuki Law Advocates."
    whatsapp_url = f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"
    return redirect(whatsapp_url)


@app.route('/api/lawyers')
def api_lawyers():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM lawyers')
    lawyers = [dict(row) for row in cursor.fetchall()]
    return jsonify(lawyers)


@app.route('/api/practice_areas')
def api_practice_areas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM practice_areas')
    areas = [dict(row) for row in cursor.fetchall()]
    return jsonify(areas)


@app.route('/api/testimonials')
def api_testimonials():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM testimonials')
    testimonials = [dict(row) for row in cursor.fetchall()]
    return jsonify(testimonials)


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found", 404


@app.errorhandler(500)
def internal_server_error(e):
    return "Internal server error", 500


if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    else:
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lawyers'")
            if not cursor.fetchone():
                init_db()

    app.run(debug=True, host='0.0.0.0', port=5000)