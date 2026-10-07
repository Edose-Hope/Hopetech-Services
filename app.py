"""Hopetech Flask application: local development and Vercel Functions."""
import datetime
import hashlib
import hmac
import ipaddress
import os
import re
import secrets
import time
from pathlib import Path
import bcrypt
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException
from catalog import COURSES, SCHEDULE
from database import connect, INTEGRITY_ERRORS

PUBLIC = Path(__file__).resolve().parent / 'public'
app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 16384
STATUSES = ('Pending', 'Confirmed', 'Completed', 'Cancelled')
DUMMY_PASSWORD = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt(rounds=12)).decode()

class InputError(ValueError): pass

def password_hash(password):
    if not isinstance(password, str) or not 12 <= len(password) or len(password.encode()) > 72:
        raise InputError('Use at least 12 characters and no more than 72 UTF-8 bytes.')
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

def password_matches(password, stored):
    if stored.startswith(('$2a$', '$2b$', '$2y$')):
        return len(password.encode()) <= 72 and bcrypt.checkpw(password.encode(), stored.encode())
    # Keep existing local scrypt accounts working without resetting user data.
    salt, old_hash = stored.split(':', 1)
    check = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return hmac.compare_digest(check, old_hash)

def text_field(data, key, maximum=200, required=True):
    value = data.get(key, '')
    if not isinstance(value, str): raise InputError('Please check your ' + key + '.')
    value = value.strip()
    if (required and not value) or len(value) > maximum:
        raise InputError('Please enter a valid ' + key + '.')
    return value

def email_field(data):
    value = text_field(data, 'email', 254).lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
        raise InputError('Please enter a valid email address.')
    return value

def payload():
    if request.mimetype != 'application/json':
        from werkzeug.exceptions import UnsupportedMediaType
        raise UnsupportedMediaType('JSON is required.')
    data = request.get_json()
    if not isinstance(data, dict): raise InputError('Invalid request.')
    return data

def current_session():
    token = request.cookies.get('hopetech_session')
    if not token or len(token) > 128: return None
    with connect() as connection:
        row = connection.execute('''SELECT sessions.*, admins.email FROM sessions
            JOIN admins ON admins.id=admin_id WHERE token=? AND expires>?''',
            (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
    return dict(row) if row else None

def authorized(mutation=False):
    from werkzeug.exceptions import Unauthorized, Forbidden
    session = current_session()
    if not session: raise Unauthorized('Please sign in to continue.')
    if mutation and not hmac.compare_digest(request.headers.get('X-CSRF-Token', ''), session['csrf']):
        raise Forbidden('Session verification failed. Refresh and try again.')
    return session

def rate_limit(kind, maximum, seconds):
    from werkzeug.exceptions import TooManyRequests
    address = request.remote_addr or 'unknown'
    if os.environ.get('VERCEL'):
        # Trust forwarding headers only on the Vercel runtime, where the edge sets them.
        address = request.headers.get('X-Vercel-Forwarded-For') or request.headers.get('X-Forwarded-For') or address
        address = address.split(',')[0].strip()
        try: address = str(ipaddress.ip_address(address))
        except ValueError: address = 'unknown'
    key = kind + ':' + hashlib.sha256(address.encode()).hexdigest()
    now = int(time.time())
    with connect() as connection:
        row = connection.execute('''INSERT INTO limits(key,count,expires) VALUES(?,1,?)
            ON CONFLICT(key) DO UPDATE SET
            count=CASE WHEN limits.expires<=? THEN 1 ELSE limits.count+1 END,
            expires=CASE WHEN limits.expires<=? THEN excluded.expires ELSE limits.expires END
            RETURNING count''', (key, now + seconds, now, now)).fetchone()
        connection.execute('DELETE FROM limits WHERE expires<?', (now,))
        count = row['count']
    if count > maximum: raise TooManyRequests('Too many attempts. Please try again later.')

@app.before_request
def check_origin():
    if request.path.startswith('/api/') and request.method in ('POST', 'PATCH', 'DELETE'):
        origin = request.headers.get('Origin')
        if origin and origin not in ('http://' + request.host, 'https://' + request.host):
            from werkzeug.exceptions import Forbidden
            raise Forbidden('Request origin rejected.')

@app.after_request
def response_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if request.path.startswith('/api/'): response.headers['Cache-Control'] = 'no-store'
    return response

@app.errorhandler(InputError)
def invalid_input(error): return jsonify(error=str(error)), 400

for error_type in INTEGRITY_ERRORS:
    app.register_error_handler(error_type, lambda error: (jsonify(error='This email is already registered for that course.'), 409))

@app.errorhandler(HTTPException)
def http_error(error):
    if request.path.startswith('/api/'): return jsonify(error=error.description), error.code
    return error

@app.errorhandler(Exception)
def unexpected_error(error):
    # Avoid logging database URLs, bound password values, cookies, or personal records.
    app.logger.error('Application operation failed (%s)', type(error).__name__)
    return jsonify(error='The service is temporarily unavailable. Please try again later.'), 503

@app.get('/api/catalog')
def catalog():
    return jsonify(courses=COURSES, schedule=SCHEDULE, sample=False, schedule_sample=True, currency='NGN')

@app.get('/api/health')
def health():
    with connect() as connection:
        connection.execute('SELECT id FROM admins LIMIT 1').fetchone()
        connection.execute('SELECT id FROM students LIMIT 1').fetchone()
        connection.execute('SELECT id FROM messages LIMIT 1').fetchone()
        connection.execute('SELECT token FROM sessions LIMIT 1').fetchone()
        connection.execute('SELECT key FROM limits LIMIT 1').fetchone()
    return jsonify(database='ready')

@app.get('/api/session')
def session_info():
    session = current_session()
    return jsonify(authenticated=bool(session), **({'email': session['email'], 'csrf': session['csrf']} if session else {}))

@app.post('/api/login')
def login():
    data = payload()
    rate_limit('login', 10, 900)
    email = email_field(data)
    password = data.get('password', '')
    if not isinstance(password, str) or not 1 <= len(password) <= 256:
        raise InputError('Please enter your password.')
    with connect() as connection:
        admin = connection.execute('SELECT * FROM admins WHERE email=?', (email,)).fetchone()
        valid = password_matches(password, admin['password'] if admin else DUMMY_PASSWORD)
        if not valid or not admin:
            from werkzeug.exceptions import Unauthorized
            raise Unauthorized('Email or password is incorrect.')
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        now = int(time.time())
        connection.execute('DELETE FROM sessions WHERE expires<?', (now,))
        connection.execute('INSERT INTO sessions(token,admin_id,csrf,expires) VALUES(?,?,?,?)',
            (hashlib.sha256(token.encode()).hexdigest(), admin['id'], csrf, now + 28800))
    response = jsonify(csrf=csrf, email=email)
    response.set_cookie('hopetech_session', token, max_age=28800, httponly=True, samesite='Strict',
                        secure=bool(os.environ.get('VERCEL')) or os.environ.get('HOPETECH_SECURE_COOKIE') == '1')
    return response

@app.post('/api/logout')
def logout():
    payload()
    session = authorized(True)
    with connect() as connection: connection.execute('DELETE FROM sessions WHERE token=?', (session['token'],))
    response = jsonify(ok=True)
    response.delete_cookie('hopetech_session', httponly=True, samesite='Strict',
                           secure=bool(os.environ.get('VERCEL')) or os.environ.get('HOPETECH_SECURE_COOKIE') == '1')
    return response

def serialize_row(row):
    return {key: value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value, datetime.datetime) else value
            for key, value in dict(row).items()}

@app.get('/api/students')
def student_list():
    authorized()
    with connect() as connection:
        rows = connection.execute('SELECT * FROM students ORDER BY id DESC').fetchall()
    return jsonify(students=[serialize_row(row) for row in rows])

@app.get('/api/messages')
def message_list():
    authorized()
    with connect() as connection:
        rows = connection.execute('SELECT * FROM messages ORDER BY id DESC').fetchall()
    return jsonify(messages=[serialize_row(row) for row in rows])

@app.post('/api/register')
@app.post('/api/students')
def add_student():
    data = payload()
    admin = request.path == '/api/students'
    if admin: authorized(True)
    else:
        rate_limit('registration', 10, 3600)
        if data.get('website'): raise InputError('Unable to submit this registration.')
        if data.get('consent') is not True: raise InputError('Please agree to the registration privacy notice.')
    name, email, phone = text_field(data, 'name', 100), email_field(data), text_field(data, 'phone', 30)
    if not re.fullmatch(r'[+\d ()-]{7,30}', phone): raise InputError('Please enter a valid phone number.')
    course, schedule = text_field(data, 'course'), text_field(data, 'schedule')
    if course not in [c['id'] for c in COURSES] or schedule not in [s['id'] for s in SCHEDULE]:
        raise InputError('Please select a valid course and learning schedule.')
    notes = text_field(data, 'notes', 2000, False)
    with connect() as connection:
        row = connection.execute('''INSERT INTO students(name,email,phone,course,schedule,notes)
            VALUES(?,?,?,?,?,?) RETURNING id''', (name, email, phone, course, schedule, notes)).fetchone()
    return jsonify(id=row['id'], message='Registration received. Our team will contact you to confirm availability and fees.'), 201

@app.route('/api/students/<int:student_id>', methods=['PATCH', 'DELETE'])
def update_student(student_id):
    data = payload()
    authorized(True)
    with connect() as connection:
        if request.method == 'DELETE':
            row = connection.execute('DELETE FROM students WHERE id=?', (student_id,))
        else:
            status = text_field(data, 'status')
            if status not in STATUSES: raise InputError('Invalid enrolment status.')
            row = connection.execute('UPDATE students SET status=? WHERE id=?', (status, student_id))
        if row.rowcount == 0:
            from werkzeug.exceptions import NotFound
            raise NotFound('Student not found.')
    return jsonify(ok=True)

@app.post('/api/contact')
def contact():
    data = payload()
    rate_limit('contact', 10, 3600)
    if data.get('website'): raise InputError('Unable to submit this message.')
    name, email, message = text_field(data, 'name', 100), email_field(data), text_field(data, 'message', 3000)
    with connect() as connection:
        connection.execute('INSERT INTO messages(name,email,message) VALUES(?,?,?)', (name, email, message))
    return jsonify(message='Your enquiry has been received. Our team will get back to you.'), 201

@app.get('/')
def home(): return send_from_directory(PUBLIC, 'index.html')

@app.get('/<path:path>')
def public_file(path):
    routes = {name: name + '.html' for name in ('about','courses','schedule','contact','register','admin')}
    return send_from_directory(PUBLIC, routes.get(path, path))
