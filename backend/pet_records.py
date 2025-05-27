import os
import json
import uuid
import shutil
from werkzeug.utils import secure_filename
from backend.data_structures.hash_table import HashTable
import logging


UPLOAD_FOLDER = 'static/uploads/pets'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

logger = logging.getLogger(__name__)

def load_pet_records():
    pets_file = 'data/pets.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    if not os.path.exists(pets_file):
        with open(pets_file, 'w') as f:
            json.dump({}, f)
    
    
    with open(pets_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_pet_records(pets_data):
    pets_file = 'data/pets.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    with open(pets_file, 'w') as f:
        json.dump(pets_data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_pet_photo(photo_file, pet_id):
    try:
        if not photo_file:
            return None
            
        if not allowed_file(photo_file.filename):
            raise ValueError("Invalid file type")
            
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        
        filename = secure_filename(photo_file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{pet_id}.{ext}"
        
        
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)
        photo_file.save(file_path)
        
        
        return os.path.join('uploads/pets', new_filename)
        
    except Exception as e:
        logger.error(f"Error saving pet photo: {str(e)}")
        return None

def add_pet(pets_data, username, pet_data, photo_file=None):
    
    if username not in pets_data:
        pets_data[username] = []
    
    
    pet_id = str(uuid.uuid4())
    
    
    pet_data['id'] = pet_id
    
    
    if photo_file:
        photo_path = save_pet_photo(photo_file, pet_id)
        if photo_path:
            pet_data['photo'] = photo_path
    
    
    pet_table = HashTable()
    
    
    pet_table.insert(pet_id, pet_data)
    
    
    pets_data[username].append(pet_data)
    
    return pet_data

def get_pet(pets_data, username, pet_id):
    if username in pets_data:
        
        pet_table = HashTable()
        
        
        for pet in pets_data[username]:
            pet_table.insert(pet['id'], pet)
        
        
        return pet_table.get(pet_id)
    return None

def update_pet(pets_data, username, pet_id, updated_data):
    if username in pets_data:
        for i, pet in enumerate(pets_data[username]):
            if pet['id'] == pet_id:
                
                updated_data['id'] = pet_id
                
                pets_data[username][i] = updated_data
                return True
    return False

def delete_pet(pets_data, username, pet_id):
    if username in pets_data:
        
        pet_table = HashTable()
        
        
        for i, pet in enumerate(pets_data[username]):
            pet_table.insert(pet['id'], (i, pet))
        
        
        result = pet_table.get(pet_id)
        if result:
            index, _ = result
            pets_data[username].pop(index)
            return True
    return False

def get_all_pets(pets_data, username):
    if username in pets_data:
        return pets_data[username]
    return []

def search_pets(pets_data, username, query):
    results = []
    query = query.lower()
    
    if username in pets_data:
        
        for pet in pets_data[username]:
            
            name = pet.get('name', '').lower()
            breed = pet.get('breed', '').lower()
            
            if query in name or query in breed:
                if pet not in results:  
                    results.append(pet)
    
    return results
