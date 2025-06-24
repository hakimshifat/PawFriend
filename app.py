import os
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import logging
import re

load_dotenv()

from backend import pet_records, appointments, reminders, emergency_locator, auth, alerts
from backend.utils import login_required
from backend.graph_nodes import get_graph_nodes

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  
app.config['UPLOAD_EXTENSIONS'] = ALLOWED_EXTENSIONS
app.config['UPLOAD_PATH'] = UPLOAD_FOLDER


app.config['USE_SYSTEM_FILE_CHOOSER'] = False


@app.errorhandler(413)
def too_large(e):
    return "File is too large. Maximum size is 16MB.", 413


@app.errorhandler(400)
def bad_request(e):
    return "Invalid file type. Allowed types: PNG, JPG, GIF, MP4, WEBM, OGG", 400


@app.context_processor
def inject_current_year():
    return {"current_year": datetime.datetime.now().year}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, subfolder=''):
    if not file:
        return False, "No file provided"
        
    if not file.filename:
        return False, "No filename provided"
        
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    try:
        filename = secure_filename(file.filename)
        
        
        date_folder = datetime.datetime.now().strftime('%Y/%m')
        if subfolder:
            upload_folder = os.path.join(UPLOAD_FOLDER, subfolder, date_folder)
        else:
            upload_folder = os.path.join(UPLOAD_FOLDER, date_folder)
            
        os.makedirs(upload_folder, exist_ok=True)
        
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        url_path = file_path.replace(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), '')
        url_path = url_path.replace('\\', '/')  
        
        return True, url_path
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False, f"Error saving file: {str(e)}"

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return "File not found", 404


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        
        users_data = auth.load_users()
        
        
        verified, message = auth.verify_user(users_data, username, password)
        
        if verified:
            
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(message, 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        
        if auth.user_exists(username) or auth.email_exists(email):
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))

        
        if auth.create_user(username, email, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        flash('Registration failed', 'danger')
        return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')
    
    
    pets_data = pet_records.load_pet_records()
    pets = pet_records.get_all_pets(pets_data, username)
    
    
    appointments_data = appointments.load_appointments()
    all_appointments = appointments.get_all_appointments(appointments_data, username)
    next_appointment = appointments.get_next_appointment(appointments_data, username)
    
    
    reminders_data = reminders.load_reminders()
    next_reminder = reminders.get_next_reminder(reminders_data, username)
    
    
    if next_appointment:
        for pet in pets:
            if pet['id'] == next_appointment['pet_id']:
                next_appointment['pet_name'] = pet['name']
                break
    
    if next_reminder:
        for pet in pets:
            if pet['id'] == next_reminder['pet_id']:
                next_reminder['pet_name'] = pet['name']
                break
    
    
    for appointment in all_appointments:
        for pet in pets:
            if pet['id'] == appointment['pet_id']:
                appointment['pet_name'] = pet['name']
                break
    
    return render_template(
        'dashboard.html',
        username=username,
        pets=pets,
        next_appointment=next_appointment,
        next_reminder=next_reminder,
        appointments=all_appointments
    )

@app.route('/pets/add', methods=['GET', 'POST'])
@login_required
def add_pet_route():
    if request.method == 'POST':
        username = session.get('username')
        
        
        pet_data = {
            'name': request.form.get('name'),
            'species': request.form.get('species'),
            'breed': request.form.get('breed'),
            'age': float(request.form.get('age')),  # <-- changed from int() to float()
            'weight': float(request.form.get('weight')),
            'medical_history': request.form.get('medical_history', ''),
            'vaccinations': [v.strip() for v in request.form.get('vaccinations', '').split(',') if v.strip()]
        }
        
        
        if pet_data['species'].lower() not in ['cat', 'dog']:
            flash("Only cats and dogs are allowed as pets in this system.", 'danger')
            return redirect(url_for('add_pet_route'))
        
        
        pets_data = pet_records.load_pet_records()
        
        
        photo_file = request.files.get('pet_photo')
        
        
        new_pet = pet_records.add_pet(pets_data, username, pet_data, photo_file)
        
        
        pet_records.save_pet_records(pets_data)
        
        flash(f"Pet '{new_pet['name']}' added successfully!", 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_pet.html')

@app.route('/pets/<pet_id>')
@login_required
def pet_profile(pet_id):
    username = session.get('username')
    
    
    pets_data = pet_records.load_pet_records()
    pet = pet_records.get_pet(pets_data, username, pet_id)
    
    if not pet:
        flash('Pet not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    
    appointments_data = appointments.load_appointments()
    pet_appointments = appointments.get_appointments_for_pet(appointments_data, username, pet_id)
    
    
    reminders_data = reminders.load_reminders()
    pet_reminders = reminders.get_reminders_for_pet(reminders_data, username, pet_id)
    
    return render_template(
        'pet_profile.html',
        pet=pet,
        pet_appointments=pet_appointments,
        pet_reminders=pet_reminders
    )

@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointment_route():
    username = session.get('username')

    vets = load_json_data('vets.json')
    slots = load_json_data('slots.json')

    if request.method == 'POST':
        appointment_data = {
            'pet_id': request.form.get('pet_id'),
            'vet_id': request.form.get('vet_id'),
            'date': request.form.get('date'),
            'slot': request.form.get('slot'),
            'reason': request.form.get('reason'),
            'priority': int(request.form.get('priority'))
        }

        appointments_data = appointments.load_appointments()
        urgent_photo = None
        if int(appointment_data['priority']) <= 2:
            urgent_photo = request.files.get('urgent_photo')

        new_appointment = appointments.add_appointment(appointments_data, username, appointment_data, urgent_photo)
        appointments.save_appointments(appointments_data)

        flash('Appointment scheduled successfully!', 'success')
        return redirect(url_for('appointment_route'))

    pets_data = pet_records.load_pet_records()
    pets = pet_records.get_all_pets(pets_data, username)
    appointments_data = appointments.load_appointments()
    all_appointments = appointments.get_all_appointments(appointments_data, username)

    for appointment in all_appointments:
        for pet in pets:
            if pet['id'] == appointment['pet_id']:
                appointment['pet_name'] = pet['name']
                break

    return render_template(
        'appointments.html',
        pets=pets,
        appointments=all_appointments,
        vets=vets,
        slots=slots
    )

@app.route('/emergency', methods=['GET', 'POST'])
@login_required
def emergency_locator_route():
    clinic_graph, clinics = emergency_locator.create_clinic_graph()
    clinics_list = [
        {
            'id': str(cid),
            'name': cdata['name'],
            'type': cdata.get('type', 'clinic'),
            'color': '#e74c3c' if cdata.get('type', 'clinic') == 'clinic' else None,
            'label': cdata['name']  # Add label for vis-network
        }
        for cid, cdata in clinics.items()
    ]
    from_id = None
    to_id = None
    nearest_clinic = None
    path_names = None
    if request.method == 'POST':
        from_id = request.form.get('from_location')
        to_id = request.form.get('to_location')
        if from_id and from_id in clinics:
            if to_id and to_id in clinics:
                # User selected a specific destination clinic
                nearest_clinic = clinics[to_id]
                nearest_id = to_id
            else:
                # Find nearest emergency clinic
                nearest_clinic, nearest_id = emergency_locator.find_nearest_clinic(clinic_graph, from_id)
            if nearest_clinic and nearest_id:
                _, path = clinic_graph.dijkstra_shortest_path(str(from_id), nearest_id)
                path_names = [clinics[pid]['name'] for pid in path if 'name' in clinics[pid]]
    # Build edges as a JSON array for the template
    edges = []
    shortest_path_edges = set()
    if path_names and request.method == 'POST' and from_id and nearest_clinic and nearest_id:
        _, path = clinic_graph.dijkstra_shortest_path(str(from_id), nearest_id)
        for i in range(len(path) - 1):
            a, b = str(path[i]), str(path[i+1])
            shortest_path_edges.add((min(a, b), max(a, b)))
    for from_id, clinic in clinics.items():
        for to_id, weight in clinic_graph.get_edges(from_id).items():
            a, b = str(from_id), str(to_id)
            edge = {"from": a, "to": b, "label": str(weight)}
            if (min(a, b), max(a, b)) in shortest_path_edges:
                edge["color"] = "#2ecc40"  # green for shortest path
                edge["width"] = 4
            if a < b:
                edges.append(edge)
    import json as _json
    edges_json = _json.dumps(edges)
    return render_template(
        'emergency_locator.html',
        clinics=clinics_list,  # for dropdowns and node list
        clinics_dict=clinics,  # for graph edges
        from_id=from_id,
        to_id=to_id,
        nearest_clinic=nearest_clinic,
        path_names=path_names,
        edges_json=edges_json
    )

@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminder_route():
    username = session.get('username')
    
    if request.method == 'POST':
        
        reminder_data = {
            'pet_id': request.form.get('pet_id'),
            'date': request.form.get('date'),
            'medication': request.form.get('medication'),
            'notes': request.form.get('notes', ''),
            'completed': False
        }
        
        
        reminders_data = reminders.load_reminders()
        
        
        new_reminder = reminders.add_reminder(reminders_data, username, reminder_data)
        
        
        reminders.save_reminders(reminders_data)
        
        flash('Reminder set successfully!', 'success')
        return redirect(url_for('reminder_route'))
    
    
    pets_data = pet_records.load_pet_records()
    pets = pet_records.get_all_pets(pets_data, username)
    
    
    reminders_data = reminders.load_reminders()
    all_reminders = reminders.get_all_reminders(reminders_data, username)
    
    
    upcoming_reminders = reminders.get_upcoming_reminders(reminders_data, username, days=7)
    
    
    appointments_data = appointments.load_appointments()
    upcoming_appointments = []
    
    
    all_appointments = appointments.get_all_appointments(appointments_data, username)
    
    
    from datetime import datetime, timedelta
    today = datetime.now().date()
    seven_days_later = today + timedelta(days=7)
    
    for appointment in all_appointments:
        appointment_date = datetime.strptime(appointment['date'], "%Y-%m-%d").date()
        if today <= appointment_date <= seven_days_later:
            upcoming_appointments.append(appointment)
    
    
    for reminder in all_reminders:
        for pet in pets:
            if pet['id'] == reminder['pet_id']:
                reminder['pet_name'] = pet['name']
                break
    
    for reminder in upcoming_reminders:
        for pet in pets:
            if pet['id'] == reminder['pet_id']:
                reminder['pet_name'] = pet['name']
                break
    
    for appointment in upcoming_appointments:
        for pet in pets:
            if pet['id'] == appointment['pet_id']:
                appointment['pet_name'] = pet['name']
                break
    
    return render_template(
        'reminders.html',
        pets=pets,
        reminders=all_reminders,
        upcoming_reminders=upcoming_reminders,
        upcoming_appointments=upcoming_appointments
    )

@app.route('/reminders/<reminder_id>/complete', methods=['POST'])
@login_required
def mark_reminder_complete(reminder_id):
    username = session.get('username')
    
    
    reminders_data = reminders.load_reminders()
    
    
    success = reminders.mark_reminder_complete(reminders_data, username, reminder_id)
    
    if success:
        
        reminders.save_reminders(reminders_data)
        flash('Reminder marked as complete!', 'success')
    else:
        flash('Reminder not found.', 'danger')
    
    
    referrer = request.referrer
    if referrer and 'dashboard' in referrer:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('reminder_route'))

@app.route('/alerts', methods=['GET', 'POST'])
@login_required
def pet_alerts():
    username = session.get('username')
    graph_nodes = get_graph_nodes()  # <-- Add this line
    
    if request.method == 'POST':
        action = request.form.get('action', 'create')
        
        if action == 'create':
            try:
                pet_type = request.form.get('pet_type')
                description = request.form.get('description')
                location_node = request.form.get('location_node')
                category = request.form.get('category')
                priority = int(request.form.get('priority', 3))
                expiration_days = int(request.form.get('expiration_days', 30))
                media_url = None
                if 'media' in request.files:
                    file = request.files['media']
                    if file and file.filename:
                        success, result = save_uploaded_file(file, subfolder='alerts')
                        if success:
                            media_url = url_for('static', filename=result.lstrip('/'))
                        else:
                            flash(f"Warning: {result}", 'warning')
                new_alert = alerts.add_alert(
                    username=username,
                    pet_type=pet_type,
                    description=description,
                    location=location_node,  # Pass node id instead of [lat, lon]
                    category=category,
                    priority=priority,
                    media_url=media_url,
                    expiration_days=expiration_days
                )
                flash('Alert posted successfully!', 'success')
                
            except ValueError as e:
                flash(str(e), 'danger')
            except Exception as e:
                logger.error(f"Error creating alert: {str(e)}")
                flash('Error creating alert. Please try again.', 'danger')
                
        elif action == 'verify':
            alert_id = int(request.form.get('alert_id'))
            if alerts.verify_alert(alert_id, username):
                contact_info = request.form.get('contact_info')
                response_text = request.form.get('response_text')
                if alerts.add_response(alert_id, username, response_text, contact_info):
                    flash('Response added successfully!', 'success')
            
        elif action == 'subscribe':
            alert_id = int(request.form.get('alert_id'))
            if alerts.subscribe_to_alert(alert_id, username):
                flash('Subscribed to alert updates!', 'success')
            
        elif action == 'update_status':
            try:
                alert_id = int(request.form.get('alert_id'))
                new_status = request.form.get('status')
                if alerts.update_alert_status(alert_id, new_status):
                    flash('Alert status updated!', 'success')
            except ValueError as e:
                flash(str(e), 'danger')
            
        elif action == 'mark_notification_read':
            notification_id = int(request.form.get('notification_id'))
            if alerts.mark_notification_read(username, notification_id):
                return jsonify({'success': True})
            return jsonify({'success': False}), 400
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        return redirect(url_for('pet_alerts'))
    
    
    category = request.args.get('category')
    view = request.args.get('view', 'all')  
    max_distance = request.args.get('max_distance')
    user_lat = request.args.get('user_lat')
    user_lon = request.args.get('user_lon')
    search_query = request.args.get('q')
    min_priority = request.args.get('min_priority', type=int)
    tags = request.args.getlist('tags')
    
    
    notifications = alerts.get_user_notifications(username)
    unread_notifications = alerts.get_user_notifications(username, unread_only=True)
    
    
    statistics = None
    if view == 'all' and not category and not search_query:
        statistics = alerts.get_alert_statistics()
    
    
    if search_query:
        all_alerts = alerts.search_alerts(search_query)
    elif category:
        all_alerts = alerts.get_alerts_by_category(category)
    elif view == 'mine':
        all_alerts = alerts.get_user_alerts(username)
    elif view == 'subscribed':
        all_alerts = alerts.get_subscribed_alerts(username)
    else:
        if max_distance and user_lat and user_lon:
            all_alerts = alerts.get_active_alerts(
                max_distance_km=float(max_distance),
                location=[float(user_lat), float(user_lon)],
                tags=tags if tags else None,
                min_priority=min_priority
            )
        else:
            all_alerts = alerts.get_active_alerts(
                tags=tags if tags else None,
                min_priority=min_priority
            )
    
    return render_template(
        'pet_alerts.html',
        alerts=all_alerts,
        categories=alerts.ALERT_CATEGORIES,
        priority_levels=alerts.PRIORITY_LEVELS,
        alert_statuses=alerts.ALERT_STATUSES,
        current_category=category,
        current_view=view,
        username=username,
        notifications=notifications,
        unread_count=len(unread_notifications),
        statistics=statistics,
        search_query=search_query,
        graph_nodes=graph_nodes  # <-- Add this line
    )

@app.route('/alerts/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    username = session.get('username')
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notifications = alerts.get_user_notifications(username, unread_only=unread_only)
    return jsonify(notifications)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def load_json_data(filename):
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', filename)
    with open(data_path, 'r') as f:
        return json.load(f)
