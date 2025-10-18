from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import uuid
import os
import logging
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'osho'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data_dir = 'data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Custom exception classes
class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = sqlite3.connect('askai.db', check_same_thread=False)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise DatabaseError(f"Failed to connect to database: {str(e)}")

def validate_input(data, required_fields):
    """Validate input data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field] or not data[field].strip():
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")

def handle_database_operation(operation_func):
    """Decorator to handle database operations with proper error handling"""
    @wraps(operation_func)
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"Database operation error: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in database operation: {str(e)}")
            raise
    return wrapper

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('error.html', 
                          error_code='404',
                          error_title='Page Not Found',
                          error_message='The page you are looking for does not exist.',
                          error_id=str(uuid.uuid4())[:8]), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    error_id = str(uuid.uuid4())[:8]
    logger.error(f"Internal server error (ID: {error_id}): {str(error)}")
    return render_template('error.html', 
                          error_code='500',
                          error_title='Internal Server Error',
                          error_message='Something went wrong on our end. Our team has been notified.',
                          error_id=error_id,
                          auto_refresh=True), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('error.html', 
                          error_code='403',
                          error_title='Access Forbidden',
                          error_message='You do not have permission to access this resource.',
                          error_id=str(uuid.uuid4())[:8]), 403

@app.errorhandler(401)
def unauthorized_error(error):
    """Handle 401 errors"""
    # Clear potentially corrupted session
    clear_session_safely()
    return render_template('error.html', 
                          error_code='401',
                          error_title='Unauthorized Access',
                          error_message='You need to be logged in to access this page.',
                          error_id=str(uuid.uuid4())[:8]), 401

@app.errorhandler(DatabaseError)
def handle_database_error(error):
    """Handle custom database errors"""
    error_id = str(uuid.uuid4())[:8]
    logger.error(f"Database error (ID: {error_id}): {str(error)}")
    flash('A database error occurred. Please try again later.', 'error')
    return render_template('error.html', 
                          error_code='DB_ERROR',
                          error_title='Database Error',
                          error_message='We are experiencing database issues. Please try again later.',
                          error_id=error_id), 500

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle validation errors"""
    clear_session_safely()  # Clear session on validation errors
    flash(str(error), 'error')
    return redirect(request.referrer or url_for('login_form'))

@handle_database_operation

@handle_database_operation
def create_tables():
    """Create database tables with error handling"""
    conn, cursor = get_db_connection()
    
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS tenants (
                            tenant_id TEXT PRIMARY KEY,
                            tenant_name TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id TEXT PRIMARY KEY,
                            user_name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT DEFAULT 'user',
                            tenant_id TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                            document_id TEXT PRIMARY KEY,
                            document_name TEXT,
                            document_type TEXT,
                            document_path TEXT,
                            tenant_id TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                            question_id TEXT PRIMARY KEY,
                            question_content TEXT NOT NULL,
                            user_id TEXT NOT NULL,
                            tenant_id TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS answers (
                            answer_id TEXT PRIMARY KEY,
                            answer_content TEXT NOT NULL,
                            user_id TEXT NOT NULL,
                            question_id TEXT NOT NULL,
                            tenant_id TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (question_id) REFERENCES questions(question_id),
                            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                            history_id TEXT PRIMARY KEY,
                            action TEXT NOT NULL,
                            user_id TEXT NOT NULL,
                            affected_id TEXT NOT NULL,
                            affected_type TEXT NOT NULL,
                            tenant_id TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users(user_id),
                            FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
                        )''')
        
        conn.commit()
        logger.info("Database tables created successfully")
    finally:
        conn.close()

@app.route('/')
def index():
    if is_logged_in():
        if session['role'] == 'admin':
            return render_template('index.html', 
                                 username=session['username'],
                                 user_role=session.get('role'),
                                 show_nav=True,
                                 show_footer=True)
        else:
            return redirect(url_for('tenant_data', tenant_id=session['tenant_id']))
    else:
        return redirect(url_for('login_form'))
    
@app.route('/create_tables')
def create_tables_route():
    create_tables()
    return redirect(url_for('login_form'))
    

@app.route('/login', methods=['GET'])
def login_form():
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET'])
def register_form():
    if is_logged_in():
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html', 
                         username=session.get('username'),
                         user_role=session.get('role'),
                         show_nav=True,
                         show_footer=True)


@app.route('/load_documents/<tenant_id>', methods=['GET'])
def load_documents(tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    user_role = session.get('role')
    if user_role == 'admin':
        home_url = '/'
    else:
        home_url = '/tenant_data/' + tenant_id
    conn, cursor = get_db_connection()
    cursor.execute('''SELECT * FROM tenants WHERE tenant_id = ?''', (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    tenant_dict = {'tenant_id': tenant[0], 'tenant_name': tenant[1], 'created_at': tenant[2], 'updated_at': tenant[3]}
    return render_template('load_documents.html', 
                         username=session.get('username'), 
                         tenant=tenant_dict, 
                         home_url=home_url,
                         user_role=session.get('role'),
                         show_nav=True,
                         show_footer=True)


@app.route('/register', methods=['POST'])
def register():
    """Register route with proper error handling and validation"""
    try:
        # Validate input
        form_data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'password': request.form.get('password', ''),
            'tenant_id': request.form.get('tenant_id', '').strip()
        }
        
        validate_input(form_data, ['username', 'email', 'password', 'tenant_id'])
        
        username = form_data['username']
        email = form_data['email']
        password = form_data['password']
        tenant_id = form_data['tenant_id']
        
        # Additional validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return redirect(url_for('register_form'))
        
        if len(password) < 4:
            flash('Password must be at least 4 characters long.', 'error')
            return redirect(url_for('register_form'))
        
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('register_form'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        user_id = str(uuid.uuid4())
        
        # Database operations
        conn, cursor = get_db_connection()
        try:
            # Check if tenant already has a user
            existing_user = cursor.execute('''SELECT * FROM users WHERE tenant_id = ?''', (tenant_id,)).fetchone()
            if existing_user is not None:
                flash('This tenant already has a user registered. Please contact administrator.', 'error')
                return redirect(url_for('register_form'))
            
            # Check if username already exists
            username_check = cursor.execute('''SELECT * FROM users WHERE user_name = ?''', (username,)).fetchone()
            if username_check is not None:
                flash('Username already exists. Please choose a different username.', 'error')
                return redirect(url_for('register_form'))
            
            # Check if email already exists
            email_check = cursor.execute('''SELECT * FROM users WHERE email = ?''', (email,)).fetchone()
            if email_check is not None:
                flash('Email already registered. Please use a different email or try logging in.', 'error')
                return redirect(url_for('register_form'))
            
            # Verify tenant exists
            tenant_check = cursor.execute('''SELECT * FROM tenants WHERE tenant_id = ?''', (tenant_id,)).fetchone()
            if tenant_check is None:
                flash('Invalid tenant ID. Please contact administrator.', 'error')
                return redirect(url_for('register_form'))
            
            # Create user
            cursor.execute('''INSERT INTO users (user_id, user_name, email, password, tenant_id) VALUES (?, ?, ?, ?, ?)''', 
                          (user_id, username, email, hashed_password, tenant_id))
            conn.commit()
            
            # Set session
            session['username'] = username
            session['user_id'] = user_id
            session['tenant_id'] = tenant_id
            session['role'] = 'user'
            
            logger.info(f"New user registered: {username} for tenant {tenant_id}")
            flash('Registration successful! Welcome to ChatMinds.', 'success')
            return redirect(url_for('tenant_data', tenant_id=tenant_id))
            
        finally:
            conn.close()
            
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('register_form'))
    except DatabaseError as e:
        logger.error(f"Database error during registration: {str(e)}")
        flash('Registration service is temporarily unavailable. Please try again later.', 'error')
        return redirect(url_for('register_form'))
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('register_form'))

# create admin user
@app.route('/seed')
def seed():
    """Create admin user with error handling"""
    try:
        conn, cursor = get_db_connection()
        try:
            admin = cursor.execute('''SELECT * FROM users WHERE user_name = ?''', ('admin',))
            if admin.fetchone() is not None:
                flash('Admin user already exists.', 'info')
                return redirect(url_for('login_form'))
            
            cursor.execute('''INSERT INTO tenants (tenant_id, tenant_name) VALUES (?, ?)''', ('1', 'admin'))
            cursor.execute('''INSERT INTO users (user_id, user_name, email, password, tenant_id, role) VALUES (?, ?, ?, ?, ?, ?)''', 
                          ('1', 'admin', 'admin@gmail.com', generate_password_hash('admin'), '1', 'admin'))
            conn.commit()
            
            logger.info("Admin user created successfully")
            flash('Admin user created successfully! You can now login with username: admin, password: admin', 'success')
            return redirect(url_for('login_form'))
            
        finally:
            conn.close()
            
    except DatabaseError as e:
        logger.error(f"Database error during admin creation: {str(e)}")
        flash('Failed to create admin user. Please try again later.', 'error')
        return redirect(url_for('login_form'))
    except Exception as e:
        logger.error(f"Unexpected error during admin creation: {str(e)}")
        flash('An unexpected error occurred while creating admin user.', 'error')
        return redirect(url_for('login_form'))


@app.route('/login', methods=['POST'])
def login():
    """Login route with proper error handling and validation"""
    if is_logged_in():
        return redirect(url_for('index'))
    
    # Clear any existing session data to prevent conflicts
    clear_session_safely()
    
    try:
        # Validate input
        form_data = {
            'username': request.form.get('username', '').strip(),
            'password': request.form.get('password', '')
        }
        
        validate_input(form_data, ['username', 'password'])
        
        username = form_data['username']
        password = form_data['password']
        
        # Additional validation
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return redirect(url_for('login_form'))
        
        if len(password) < 4:
            flash('Password must be at least 4 characters long.', 'error')
            return redirect(url_for('login_form'))
        
        # Database operations
        conn, cursor = get_db_connection()
        try:
            user = cursor.execute('''SELECT * FROM users WHERE user_name = ?''', (username,)).fetchone()
            
            if user is None:
                flash('Invalid username or password. Please check your credentials and try again.', 'error')
                logger.warning(f"Failed login attempt for non-existent user: {username}")
                return redirect(url_for('login_form'))
            
            if not check_password_hash(user[3], password):
                flash('Invalid username or password. Please check your credentials and try again.', 'error')
                logger.warning(f"Failed login attempt for user: {username} (incorrect password)")
                return redirect(url_for('login_form'))
            
            # Successful login - set session data
            session['username'] = username
            session['user_id'] = user[0]
            session['tenant_id'] = user[5]
            
            if user[4] == 'admin':
                session['role'] = 'admin'
                logger.info(f"Admin user {username} logged in successfully")
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('index'))
            else:
                session['role'] = 'user'
                logger.info(f"User {username} logged in successfully")
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('tenant_data', tenant_id=user[5]))
                
        finally:
            conn.close()
            
    except ValidationError as e:
        clear_session_safely()  # Clear session on validation error
        flash(str(e), 'error')
        return redirect(url_for('login_form'))
    except DatabaseError as e:
        clear_session_safely()  # Clear session on database error
        logger.error(f"Database error during login: {str(e)}")
        flash('Login service is temporarily unavailable. Please try again later.', 'error')
        return redirect(url_for('login_form'))
    except Exception as e:
        clear_session_safely()  # Clear session on any unexpected error
        logger.error(f"Unexpected error during login: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('login_form'))

@app.route('/logout')
def logout():
    """Logout route with proper session cleanup"""
    username = session.get('username', 'Unknown user')
    clear_session_safely()
    logger.info(f"User {username} logged out successfully")
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login_form'))


def is_logged_in():
    """Check if user is logged in and session is valid"""
    if 'username' not in session:
        return False
    
    # Additional session validation
    required_session_keys = ['username', 'user_id', 'tenant_id', 'role']
    for key in required_session_keys:
        if key not in session:
            # Session is corrupted, clear it
            session.clear()
            return False
    
    return True

def clear_session_safely():
    """Safely clear session data"""
    session.clear()
    logger.info("Session cleared due to error or logout")

@app.before_request
def check_session_integrity():
    """Check session integrity before each request"""
    # Skip session check for static files and auth routes
    if request.endpoint in ['static', 'login_form', 'login', 'register_form', 'register', 'seed', 'create_tables_route']:
        return
    
    # If user claims to be logged in but session is incomplete, clear it
    if 'username' in session:
        required_keys = ['username', 'user_id', 'tenant_id', 'role']
        missing_keys = [key for key in required_keys if key not in session]
        if missing_keys:
            logger.warning(f"Corrupted session detected, missing keys: {missing_keys}")
            clear_session_safely()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login_form'))


@app.route('/add_tenant', methods=['POST'])
def add_tenant():
    """Add tenant with error handling and validation"""
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    try:
        # Validate input
        tenant_name = request.form.get('tenant_name', '').strip()
        if not tenant_name:
            return jsonify({'error': 'Tenant name is required'}), 400
        
        if len(tenant_name) < 2:
            return jsonify({'error': 'Tenant name must be at least 2 characters long'}), 400
        
        tenant_id = str(uuid.uuid4())
        
        # Database operations
        conn, cursor = get_db_connection()
        try:
            # Check if tenant name already exists
            existing_tenant = cursor.execute('''SELECT * FROM tenants WHERE tenant_name = ?''', (tenant_name,)).fetchone()
            if existing_tenant is not None:
                return jsonify({'error': 'Tenant name already exists'}), 400
            
            cursor.execute('''INSERT INTO tenants (tenant_id, tenant_name) VALUES (?, ?)''', (tenant_id, tenant_name))
            conn.commit()
            
            logger.info(f"New tenant created: {tenant_name} (ID: {tenant_id})")
            return jsonify({'message': 'Tenant added successfully', 'tenant_id': tenant_id}), 201
            
        finally:
            conn.close()
            
    except DatabaseError as e:
        logger.error(f"Database error while adding tenant: {str(e)}")
        return jsonify({'error': 'Failed to add tenant due to database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error while adding tenant: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/get_all_tenants', methods=['GET'])
def get_all_tenants():
    """Get all tenants with error handling"""
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    try:
        conn, cursor = get_db_connection()
        try:
            cursor.execute('''SELECT tenant_id, tenant_name, created_at, updated_at FROM tenants WHERE tenant_name != 'admin';''')
            tenants = cursor.fetchall()
            
            tenant_list = [{'tenant_id': t[0], 'tenant_name': t[1], 'created_at': t[2], 'updated_at': t[3]} for t in tenants]
            return jsonify(tenant_list), 200
            
        finally:
            conn.close()
            
    except DatabaseError as e:
        logger.error(f"Database error while fetching tenants: {str(e)}")
        return jsonify({'error': 'Failed to fetch tenants due to database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error while fetching tenants: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/edit_tenant/<tenant_id>', methods=['PUT'])
def edit_tenant(tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    new_tenant_name = request.form['new_tenant_name']
    conn, cursor = get_db_connection()
    cursor.execute('''UPDATE tenants SET tenant_name = ?, updated_at = CURRENT_TIMESTAMP WHERE tenant_id = ?''', (new_tenant_name, tenant_id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tenant updated successfully'}), 200


@app.route('/delete_tenant/<tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    conn, cursor = get_db_connection()
    cursor.execute('''DELETE FROM tenants WHERE tenant_id = ?''', (tenant_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Tenant deleted successfully'}), 200
    

@app.route('/tenant_data/<tenant_id>', methods=['GET'])
def tenant_data(tenant_id):
    """Get tenant data with error handling"""
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    try:
        # Validate tenant_id
        if not tenant_id or not tenant_id.strip():
            flash('Invalid tenant ID provided.', 'error')
            return redirect(url_for('index'))
        
        user_role = session.get('role')
        if user_role == 'admin':
            home_url = '/'
        else:
            home_url = '/tenant_data/' + tenant_id
        
        # Database operations
        conn, cursor = get_db_connection()
        try:
            cursor.execute('''SELECT * FROM tenants WHERE tenant_id = ?''', (tenant_id,))
            tenant = cursor.fetchone()
            
            if tenant is None:
                flash('Tenant not found. Please check the tenant ID.', 'error')
                logger.warning(f"Attempted access to non-existent tenant: {tenant_id}")
                return render_template('error.html', 
                                      error_code='404',
                                      error_title='Tenant Not Found',
                                      error_message='The requested tenant does not exist.')
            
            tenant_dict = {
                'tenant_id': tenant[0], 
                'tenant_name': tenant[1], 
                'created_at': tenant[2], 
                'updated_at': tenant[3]
            }
            
            return render_template('tenant_data.html', 
                                 tenant=tenant_dict, 
                                 username=session['username'], 
                                 user_profile_url='/get_user/'+session['user_id'],  
                                 home_url=home_url, 
                                 base_path=os.path.dirname(os.path.abspath(__file__)),
                                 user_role=session.get('role'),
                                 show_nav=True,
                                 show_footer=True)
            
        finally:
            conn.close()
            
    except DatabaseError as e:
        logger.error(f"Database error while fetching tenant data: {str(e)}")
        flash('Unable to load tenant data. Please try again later.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Unexpected error while fetching tenant data: {str(e)}")
        flash('An unexpected error occurred.', 'error')
        return redirect(url_for('index'))
    

@app.route('/documents/<tenant_id>', methods=['GET'])
def get_documents(tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    conn, cursor = get_db_connection()
    tenant = cursor.execute('''SELECT * FROM tenants WHERE tenant_id = ?''', (tenant_id,))
    if tenant.fetchone() is None:
        return render_template('tenant_data', message='Tenant not found')
    cursor.execute('''SELECT * FROM documents WHERE tenant_id = ?''', (tenant_id,))
    documents = cursor.fetchall()
    conn.close()
    document_list = [{'document_id': d[0], 'document_name': d[1], 'document_type': d[2], 'document_path': '\\'+d[3], 'created_at': d[5], 'updated_at': d[6]} for d in documents]
    return jsonify(document_list), 200

@app.route('/storage/<tenant_id>', methods=['GET'])
def get_storage_usage(tenant_id):
    """Calculate and return storage usage for a tenant"""
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    try:
        # Calculate tenant storage usage
        tenant_dir = os.path.join(data_dir, tenant_id)
        total_size = 0
        file_count = 0
        
        if os.path.exists(tenant_dir):
            for root, dirs, files in os.walk(tenant_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                    except (OSError, IOError):
                        # Skip files that can't be accessed
                        continue
        
        # Format size in human readable format
        def format_bytes(bytes):
            if bytes == 0:
                return "0 B"
            
            import math
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = int(math.floor(math.log(bytes, 1024)))
            p = math.pow(1024, i)
            s = round(bytes / p, 2)
            return f"{s} {size_names[i]}"
        
        formatted_size = format_bytes(total_size)
        
        return jsonify({
            'total_bytes': total_size,
            'formatted_size': formatted_size,
            'file_count': file_count
        }), 200
    
    except Exception as e:
        logging.error(f"Error calculating storage usage for tenant {tenant_id}: {str(e)}")
        return jsonify({
            'total_bytes': 0,
            'formatted_size': '0 B',
            'file_count': 0
        }), 200


@app.route('/add_document/<tenant_id>', methods=['POST'])
def add_document(tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    if tenant_id is None:
        return jsonify({'message': 'Tenant ID is required'}), 400
    
    if 'files[]' not in request.files:
        return {"error": "No file part in the request."}, 400
    
    files = request.files.getlist('files[]')
    if not files:
        return jsonify({'message': 'No files provided'}), 400
    
    tenant_dir = os.path.join(data_dir, tenant_id)
    docs_dir = os.path.join(tenant_dir, 'docs')
    raw_dir = os.path.join(docs_dir, 'raw')
    clean_dir = os.path.join(docs_dir, 'clean')
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)
    if not os.path.exists(clean_dir):
        os.makedirs(clean_dir)

    for file in files:

        # Extract document_id from the filename
        filename = secure_filename(file.filename)
        parts = filename.split('_')
        if len(parts) < 2:
            return jsonify({'error': 'Invalid filename format'}), 400
        
        document_id = parts[0]
        document_name = '_'.join(parts[1:])
        file_extension = filename.split('.')[-1]
        full_filename = f'{document_id}.{file_extension}'

        mime_type = file.content_type
        document_path = os.path.join(raw_dir, full_filename)
        file.save(document_path)
        conn, cursor = get_db_connection()
        cursor.execute('''INSERT INTO documents (document_id, document_name, document_type, document_path, tenant_id) VALUES (?, ?, ?, ?, ?)''', (document_id, document_name, mime_type, document_path, tenant_id))
        conn.commit()
        conn.close()
    return jsonify({'message': 'Document added successfully'}), 201


@app.route('/delete_document/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    conn, cursor = get_db_connection()
    cursor.execute('''DELETE FROM documents WHERE document_id = ?''', (document_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Document deleted successfully'}), 200


@app.route('/view_document/<document_id>/tenant/<tenant_id>', methods=['GET'])
def view_document(document_id, tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    conn, cursor = get_db_connection()
    cursor.execute('''SELECT * FROM documents WHERE document_id = ? AND tenant_id = ?''', (document_id, tenant_id))
    document = cursor.fetchone()
    conn.close()
    if document is None:
        return render_template('tenant_data', message='Document not found')
    mimetype = document[2]
    if mimetype.startswith('application/pdf'):
        file_extension = 'pdf'
    elif mimetype.startswith('text/plain'):
        file_extension = 'txt'

    # Construct the file path based on the provided information
    file_path = os.path.join('data', tenant_id, 'docs', 'raw', f'{document_id}.{file_extension}')
    if not os.path.exists(file_path):
        return 'File not found', 404
    
    # Send the file using Flask's send_file function
    return send_file(file_path, as_attachment=False)


@app.route('/view_cleaned_document/<document_id>/tenant/<tenant_id>', methods=['GET'])
def view_cleaned_document(document_id, tenant_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    # Construct the cleaned file path
    clean_file_path = os.path.join('data', tenant_id, 'docs', 'clean', f'{document_id}_cleaned.txt')
    
    if not os.path.exists(clean_file_path):
        return 'Cleaned document not found', 404
    
    # Send the cleaned file
    return send_file(clean_file_path, as_attachment=False, mimetype='text/plain')


# Route for getting all users (for admin)
@app.route('/users', methods=['GET'])
def get_all_users():
    if not is_logged_in() or session['role'] != 'admin':
        return redirect(url_for('login_form'))
    
    # Connect to the database
    conn, cursor = get_db_connection()
    # Retrieve all users from the database
    cursor.execute('''SELECT * FROM users''')
    users = cursor.fetchall()
    conn.close()
    
    # Construct user list
    user_list = []
    for user in users:
        user_info = {
            'user_id': user[0],
            'user_name': user[1],
            'email': user[2],
            'role': user[4],
            'tenant_id': user[5],
            'created_at': user[6],
            'updated_at': user[7]
        }
        user_list.append(user_info)
    
    return render_template('user_data.html', 
                         users=user_list, 
                         username=session['username'],
                         user_role=session.get('role'),
                         show_nav=True,
                         show_footer=True)


@app.route('/get_user/<user_id>', methods=['GET'])
def get_user(user_id):
    if not is_logged_in():
        return redirect(url_for('login_form'))
    
    conn, cursor = get_db_connection()
    user = cursor.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    conn.close()
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    user_info = {
        'user_id': user[0],
        'user_name': user[1],
        'email': user[2],
        'role': user[4],
        'tenant_id': user[5],
        'created_at': user[6],
        'updated_at': user[7]
    }
    return render_template('user_profile.html', 
                         user=user_info,
                         username=session.get('username'),
                         user_role=session.get('role'),
                         show_nav=True,
                         show_footer=True)


# Route for deleting a user
@app.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if not is_logged_in() or session['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 401
    
    # Connect to the database
    conn, cursor = get_db_connection()
    
    # Check if the user exists
    user = cursor.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,)).fetchone()
    if user is None:
        conn.close()
        return jsonify({'message': 'User not found'}), 404
    
    # Delete the user
    cursor.execute('''DELETE FROM users WHERE user_id = ?''', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User deleted successfully'}), 200


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker and load balancers"""
    try:
        # Check database connection
        conn, cursor = get_db_connection()
        cursor.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'service': 'chatminds-web',
            'timestamp': str(datetime.utcnow()),
            'version': '1.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'chatminds-web',
            'error': str(e),
            'timestamp': str(datetime.utcnow())
        }), 503

    
if __name__ == '__main__':
    # Initialize database tables
    create_tables()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)