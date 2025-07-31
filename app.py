
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
import os
import json
from datetime import datetime
import secrets

# Try to import database dependencies
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from dotenv import load_dotenv
    load_dotenv()
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration
GALLERY_FOLDER = 'static/galleries'
SELECTIONS_FOLDER = 'selections'
PASSWORDS_FILE = 'gallery_passwords.json'

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL') if DATABASE_AVAILABLE else None
USE_DATABASE = DATABASE_URL is not None

# Ensure directories exist for local mode
os.makedirs(GALLERY_FOLDER, exist_ok=True)
os.makedirs(SELECTIONS_FOLDER, exist_ok=True)

def get_db_connection():
    if not USE_DATABASE:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except:
        return None

def init_db():
    if not USE_DATABASE:
        return
    
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        cur = conn.cursor()
        
        # Create galleries table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS galleries (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create selections table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS selections (
                id SERIAL PRIMARY KEY,
                gallery_name VARCHAR(255) NOT NULL,
                selected_images JSON NOT NULL,
                comments JSON,
                admin_session_id VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization failed: {e}")

# Initialize database if available
init_db()

def load_passwords():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT name, password FROM galleries WHERE password IS NOT NULL")
    galleries = cur.fetchall()
    cur.close()
    conn.close()
    
    return {gallery['name']: gallery['password'] for gallery in galleries}

def save_single_gallery_password(gallery_name, password):
    """Save a single gallery password to both systems"""
    # Update JSON file
    passwords = load_passwords()
    if password:
        passwords[gallery_name] = password
    else:
        passwords.pop(gallery_name, None)
    
    with open(PASSWORDS_FILE, 'w') as f:
        json.dump(passwords, f, indent=2)
    
    # Update database if available
    if USE_DATABASE:
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                if password:
                    cur.execute('''
                        INSERT INTO galleries (name, password) 
                        VALUES (%s, %s) 
                        ON CONFLICT (name) 
                        DO UPDATE SET password = EXCLUDED.password
                    ''', (gallery_name, password))
                else:
                    cur.execute('DELETE FROM galleries WHERE name = %s', (gallery_name,))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            print(f"Database update failed: {e}")

def get_galleries():
    """Get galleries from filesystem (works both locally and online)"""
    try:
        galleries = [d for d in os.listdir(GALLERY_FOLDER) if os.path.isdir(os.path.join(GALLERY_FOLDER, d))]
        return galleries
    except:
        # If filesystem not available, try database
        if USE_DATABASE:
            try:
                conn = get_db_connection()
                if conn:
                    cur = conn.cursor(cursor_factory=RealDictCursor)
                    cur.execute("SELECT DISTINCT name FROM galleries ORDER BY created_at DESC")
                    galleries = cur.fetchall()
                    cur.close()
                    conn.close()
                    return [gallery['name'] for gallery in galleries]
            except:
                pass
        return []



def save_selection_data(selection_data):
    """Save selection to both JSON file and database"""
    gallery_name = selection_data['gallery_name']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to JSON file (local compatibility)
    try:
        filename = f"{gallery_name}_{timestamp}.json"
        filepath = os.path.join(SELECTIONS_FOLDER, filename)
        with open(filepath, 'w') as f:
            json.dump(selection_data, f, indent=2)
    except Exception as e:
        print(f"JSON save failed: {e}")
    
    # Save to database if available
    if USE_DATABASE:
        try:
            conn = get_db_connection()
            if conn:
                cur = conn.cursor()
                cur.execute('''
                    INSERT INTO selections (gallery_name, selected_images, comments, admin_session_id, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (
                    selection_data['gallery_name'],
                    json.dumps(selection_data['selected_images']),
                    json.dumps(selection_data.get('comments', {})),
                    selection_data.get('admin_session_id'),
                    datetime.fromisoformat(selection_data['timestamp'])
                ))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            print(f"Database selection save failed: {e}")

@app.route('/')
def index():
    galleries = get_galleries()
    passwords = load_passwords()
    return render_template('index.html', galleries=galleries, passwords=passwords)

@app.route('/gallery/<gallery_name>')
def gallery_login(gallery_name):
    passwords = load_passwords()
    
    # If gallery has no password, go directly to gallery
    if gallery_name not in passwords:
        return redirect(url_for('gallery', gallery_name=gallery_name))
    
    # If gallery has password but user is already authenticated
    if gallery_name in session.get('authenticated_galleries', []):
        return redirect(url_for('gallery', gallery_name=gallery_name))
    
    # Show login page for password-protected galleries
    return render_template('login.html', gallery_name=gallery_name)

@app.route('/authenticate/<gallery_name>', methods=['POST'])
def authenticate(gallery_name):
    password = request.form.get('password')
    passwords = load_passwords()
    
    if gallery_name in passwords and passwords[gallery_name] == password:
        if 'authenticated_galleries' not in session:
            session['authenticated_galleries'] = []
        
        # Avoid duplicates - this is the key fix
        if gallery_name not in session['authenticated_galleries']:
            session['authenticated_galleries'].append(gallery_name)
        
        # Force session to save
        session.modified = True
        
        return redirect(url_for('gallery', gallery_name=gallery_name))
    
    return render_template('login.html', gallery_name=gallery_name, error="Invalid password")

@app.route('/view/<gallery_name>')
def gallery(gallery_name):
    passwords = load_passwords()
    
    # Check if gallery requires password and user is not authenticated
    if gallery_name in passwords and gallery_name not in session.get('authenticated_galleries', []):
        return redirect(url_for('gallery_login', gallery_name=gallery_name))
    
    gallery_path = os.path.join(GALLERY_FOLDER, gallery_name)
    if not os.path.exists(gallery_path):
        return "Gallery not found", 404
    
    images = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    images.sort()
    
    return render_template('gallery.html', gallery_name=gallery_name, images=images)

@app.route('/submit_selection', methods=['POST'])
def submit_selection():
    data = request.json
    gallery_name = data['gallery_name']
    selections = data['selections']
    comments = data.get('comments', {})
    
    selection_data = {
        'gallery_name': gallery_name,
        'timestamp': datetime.now().isoformat(),
        'selected_images': selections,
        'comments': comments,
        'total_selected': len(selections),
        'admin_session_id': session.get('admin_session_id')
    }
    
    save_selection_data(selection_data)
    return jsonify({'success': True, 'message': 'Selection saved successfully!'})

@app.route('/static/galleries/<gallery_name>/<filename>')
def serve_image(gallery_name, filename):
    return send_from_directory(os.path.join(GALLERY_FOLDER, gallery_name), filename)

@app.route('/admin')
def admin_login():
    if session.get('admin_authenticated'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/admin/authenticate', methods=['POST'])
def admin_authenticate():
    password = request.form.get('password')
    # Simple admin password - change this to something secure
    if password == 'admin123':
        session['admin_authenticated'] = True
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html', error="Invalid admin password")

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    # Create unique session ID for this admin session
    if 'admin_session_id' not in session:
        session['admin_session_id'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    current_session_id = session['admin_session_id']
    
    galleries = get_galleries()
    passwords = load_passwords()
    
    # Get gallery stats
    gallery_stats = {}
    for gallery in galleries:
        gallery_path = os.path.join(GALLERY_FOLDER, gallery)
        image_count = len([f for f in os.listdir(gallery_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))])
        gallery_stats[gallery] = image_count
    
    # Get recent selections (last 10)
    recent_selections = []
    if os.path.exists(SELECTIONS_FOLDER):
        selection_files = [f for f in os.listdir(SELECTIONS_FOLDER) if f.endswith('.json')]
        selection_files.sort(key=lambda x: os.path.getmtime(os.path.join(SELECTIONS_FOLDER, x)), reverse=True)
        
        for filename in selection_files[:10]:  # Last 10 submissions
            filepath = os.path.join(SELECTIONS_FOLDER, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Mark if submitted during current admin session
                data['is_new'] = data.get('admin_session_id') == current_session_id
                recent_selections.append(data)
    
    return render_template('admin_dashboard.html', 
                         galleries=galleries, 
                         passwords=passwords, 
                         gallery_stats=gallery_stats,
                         recent_selections=recent_selections)

@app.route('/admin/create_gallery', methods=['POST'])
def admin_create_gallery():
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    gallery_name = request.form.get('gallery_name')
    password = request.form.get('password')
    
    if not gallery_name:
        return jsonify({'success': False, 'message': 'Gallery name required'})
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO galleries (name, password) 
            VALUES (%s, %s)
        ''', (gallery_name, password))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Gallery "{gallery_name}" created successfully'})
    except psycopg2.IntegrityError:
        return jsonify({'success': False, 'message': 'Gallery already exists'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))

@app.route('/admin/selections/<gallery_name>')
def admin_view_selections(gallery_name):
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    # Get all selection files for this gallery
    selection_files = []
    if os.path.exists(SELECTIONS_FOLDER):
        for filename in os.listdir(SELECTIONS_FOLDER):
            if filename.startswith(f"{gallery_name}_") and filename.endswith('.json'):
                filepath = os.path.join(SELECTIONS_FOLDER, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    data['filename'] = filename
                    selection_files.append(data)
    
    # Sort by timestamp (newest first)
    selection_files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('admin_selections.html', 
                         gallery_name=gallery_name, 
                         selections=selection_files)

@app.route('/admin/upload/<gallery_name>', methods=['POST'])
def admin_upload_images(gallery_name):
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if 'images' not in request.files:
        return jsonify({'success': False, 'message': 'No files selected'})
    
    files = request.files.getlist('images')
    gallery_path = os.path.join(GALLERY_FOLDER, gallery_name)
    
    if not os.path.exists(gallery_path):
        return jsonify({'success': False, 'message': 'Gallery not found'})
    
    # Extract client lastname from gallery name (assumes format like "client_smith")
    client_lastname = gallery_name.split('_')[-1] if '_' in gallery_name else gallery_name
    
    # Get existing image count to continue numbering
    existing_images = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    next_number = len(existing_images) + 1
    
    uploaded_count = 0
    for file in files:
        if file.filename and file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            # Get file extension
            original_extension = os.path.splitext(file.filename)[1].lower()
            
            # Generate new filename: {client_lastname}_{number}.{extension}
            new_filename = f"{client_lastname}_{next_number:03d}{original_extension}"
            
            # Save with new filename
            file.save(os.path.join(gallery_path, new_filename))
            uploaded_count += 1
            next_number += 1
    
    return jsonify({'success': True, 'message': f'Uploaded {uploaded_count} images successfully'})

@app.route('/admin/delete_image/<gallery_name>/<filename>', methods=['POST'])
def admin_delete_image(gallery_name, filename):
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    gallery_path = os.path.join(GALLERY_FOLDER, gallery_name)
    image_path = os.path.join(gallery_path, filename)
    
    if not os.path.exists(image_path):
        return jsonify({'success': False, 'message': 'Image not found'})
    
    try:
        os.remove(image_path)
        return jsonify({'success': True, 'message': f'Image "{filename}" deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete image: {str(e)}')

@app.route('/admin/manage_gallery/<gallery_name>')
def admin_manage_gallery(gallery_name):
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    gallery_path = os.path.join(GALLERY_FOLDER, gallery_name)
    if not os.path.exists(gallery_path):
        return "Gallery not found", 404
    
    images = [f for f in os.listdir(gallery_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    images.sort()
    
    return render_template('admin_manage_gallery.html', gallery_name=gallery_name, images=images)

@app.route('/admin/delete_gallery/<gallery_name>', methods=['POST'])
def admin_delete_gallery(gallery_name):
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        # Remove directory if possible (local)
        gallery_path = os.path.join(GALLERY_FOLDER, gallery_name)
        if os.path.exists(gallery_path):
            import shutil
            shutil.rmtree(gallery_path)
        
        # Remove password from both systems
        save_single_gallery_password(gallery_name, None)
        
        return jsonify({'success': True, 'message': f'Gallery "{gallery_name}" deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to delete gallery: {str(e)}')

@app.route('/debug/session')
def debug_session():
    if not app.debug:
        return "Debug mode only", 403
    return jsonify({
        'authenticated_galleries': session.get('authenticated_galleries', []),
        'admin_authenticated': session.get('admin_authenticated', False)
    })

@app.route('/clear_session')
def clear_session():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin/get_recent_selections')
def admin_get_recent_selections():
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    current_session_id = session.get('admin_session_id')
    
    recent_selections = []
    if os.path.exists(SELECTIONS_FOLDER):
        selection_files = [f for f in os.listdir(SELECTIONS_FOLDER) if f.endswith('.json')]
        selection_files.sort(key=lambda x: os.path.getmtime(os.path.join(SELECTIONS_FOLDER, x)), reverse=True)
        
        for filename in selection_files[:10]:
            filepath = os.path.join(SELECTIONS_FOLDER, filename)
            with open(filepath, 'r') as f:
                data = json.load(f)
                data['is_new'] = data.get('admin_session_id') == current_session_id
                recent_selections.append(data)
    
    return jsonify({'success': True, 'selections': recent_selections})

if __name__ == '__main__':
    app.run(debug=False)

# For Vercel, also add this:
# This is the WSGI entry point
application = app
