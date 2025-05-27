import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from backend.data_structures.min_heap import MinHeap
import logging


UPLOAD_FOLDER = 'static/uploads/appointments'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

logger = logging.getLogger(__name__)

def load_appointments():
    appointments_file = 'data/appointments.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    if not os.path.exists(appointments_file):
        with open(appointments_file, 'w') as f:
            json.dump({}, f)
    
    
    with open(appointments_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_appointments(appointments_data):
    appointments_file = 'data/appointments.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    with open(appointments_file, 'w') as f:
        json.dump(appointments_data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_urgent_photo(photo_file, appointment_id):
    try:
        if not photo_file:
            return None
            
        if not allowed_file(photo_file.filename):
            raise ValueError("Invalid file type")
            
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        
        filename = secure_filename(photo_file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{appointment_id}.{ext}"
        
        
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        photo_file.save(file_path)
        
        
        return os.path.join('uploads/appointments', new_filename)
        
    except Exception as e:
        logger.error(f"Error saving urgent photo: {str(e)}")
        return None

def add_appointment(appointments_data, username, appointment_data, urgent_photo=None):
    
    if username not in appointments_data:
        appointments_data[username] = []
    
    
    appointment_id = str(uuid.uuid4())
    
    
    appointment_data['id'] = appointment_id
    
    
    priority = int(appointment_data.get('priority', 3))
    if (priority == 1 or priority == 2) and urgent_photo:
        photo_path = save_urgent_photo(urgent_photo, appointment_id)
        if photo_path:
            appointment_data['urgent_photo'] = photo_path
    
    
    appointments_data[username].append(appointment_data)
    
    
    heap = MinHeap()
    heap.heapify(appointments_data[username])
    appointments_data[username] = heap.get_all_sorted()
    
    return appointment_data

def get_next_appointment(appointments_data, username):
    if username in appointments_data and appointments_data[username]:
        
        heap = MinHeap()
        heap.heapify(appointments_data[username])
        
        
        return heap.get_min()
    return None

def get_all_appointments(appointments_data, username):
    if username in appointments_data:
        
        heap = MinHeap()
        heap.heapify(appointments_data[username])
        return heap.get_all_sorted()
    return []

def delete_appointment(appointments_data, username, appointment_id):
    if username in appointments_data:
        for i, appointment in enumerate(appointments_data[username]):
            if appointment['id'] == appointment_id:
                
                appointments_data[username].pop(i)
                return True
    return False

def get_appointments_for_pet(appointments_data, username, pet_id):
    results = []
    
    if username in appointments_data:
        for appointment in appointments_data[username]:
            if appointment['pet_id'] == pet_id:
                results.append(appointment)
    
    
    heap = MinHeap()
    heap.heapify(results)
    return heap.get_all_sorted()

def get_appointments_by_date_range(appointments_data, username, start_date, end_date):
    results = []
    
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    if username in appointments_data:
        for appointment in appointments_data[username]:
            appt_date = datetime.strptime(appointment['date'], "%Y-%m-%d")
            if start <= appt_date <= end:
                results.append(appointment)
    
    
    heap = MinHeap()
    heap.heapify(results)
    return heap.get_all_sorted()
