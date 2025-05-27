import os
import json
import uuid
from datetime import datetime
from backend.data_structures.queue import Queue

def load_reminders():
    reminders_file = 'data/reminders.json'
    os.makedirs('data', exist_ok=True)
    
    if not os.path.exists(reminders_file):
        with open(reminders_file, 'w') as f:
            json.dump({}, f)
    
    with open(reminders_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
def save_reminders(reminders_data):
    reminders_file = 'data/reminders.json'
    os.makedirs('data', exist_ok=True)
    
    with open(reminders_file, 'w') as f:
        json.dump(reminders_data, f, indent=2)

def add_reminder(reminders_data, username, reminder_data):
    
    if username not in reminders_data:
        reminders_data[username] = []
    
    
    reminder_id = str(uuid.uuid4())
    
    
    reminder_data['id'] = reminder_id
    
    
    reminders_data[username].append(reminder_data)
    
    
    reminder_queue = Queue()
    for reminder in reminders_data[username]:
        reminder_queue.enqueue(reminder)
    reminder_queue.sort_by_date()
    
    
    reminders_data[username] = reminder_queue.get_all()
    
    return reminder_data

def get_next_reminder(reminders_data, username):
    if username in reminders_data and reminders_data[username]:
        
        reminder_queue = Queue()
        for reminder in reminders_data[username]:
            reminder_queue.enqueue(reminder)
        
        
        active_queue = reminder_queue.filter_by_completion(completed=False)
        
        
        active_queue.sort_by_date()
        
        
        if active_queue.size() > 0:
            return active_queue.peek()
    
    return None

def get_all_reminders(reminders_data, username):
    if username in reminders_data:
        
        reminder_queue = Queue()
        for reminder in reminders_data[username]:
            reminder_queue.enqueue(reminder)
        
        
        reminder_queue.sort_by_date()
        
        return reminder_queue.get_all()
    return []

def mark_reminder_complete(reminders_data, username, reminder_id):
    if username in reminders_data:
        for i, reminder in enumerate(reminders_data[username]):
            if reminder['id'] == reminder_id:
                reminders_data[username][i]['completed'] = True
                return True
    return False

def delete_reminder(reminders_data, username, reminder_id):
    if username in reminders_data:
        for i, reminder in enumerate(reminders_data[username]):
            if reminder['id'] == reminder_id:
                
                reminders_data[username].pop(i)
                return True
    return False

def get_reminders_for_pet(reminders_data, username, pet_id):
    results = Queue()
    
    if username in reminders_data:
        for reminder in reminders_data[username]:
            if reminder['pet_id'] == pet_id:
                results.enqueue(reminder)
    
    
    results.sort_by_date()
    
    return results.get_all()

def get_upcoming_reminders(reminders_data, username, days=7):
    if username not in reminders_data:
        return []
        
    
    reminder_queue = Queue()
    for reminder in reminders_data[username]:
        reminder_queue.enqueue(reminder)
    
    
    upcoming_queue = reminder_queue.get_upcoming(days)
    
    return upcoming_queue.get_all()
