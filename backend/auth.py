import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def load_users():
    users_file = 'data/users.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    if not os.path.exists(users_file):
        with open(users_file, 'w') as f:
            json.dump({}, f)
    
    
    with open(users_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users_data):
    users_file = 'data/users.json'
    
    
    os.makedirs('data', exist_ok=True)
    
    
    with open(users_file, 'w') as f:
        json.dump(users_data, f, indent=2)

def register_user(users_data, username, password):
    
    if username in users_data:
        return False, "Username already exists"
    
    
    password_hash = generate_password_hash(password)
    
    
    users_data[username] = {
        "username": username,
        "password_hash": password_hash
    }
    
    return True, "User registered successfully"

def verify_user(users_data, username, password):
    
    if username not in users_data:
        return False, "Invalid username or password"
    
    
    user = users_data[username]
    if not check_password_hash(user["password_hash"], password):
        return False, "Invalid username or password"
    
    return True, "Login successful"

def update_password(users_data, username, old_password, new_password):
    
    verified, message = verify_user(users_data, username, old_password)
    if not verified:
        return False, message
    
    
    new_password_hash = generate_password_hash(new_password)
    
    
    users_data[username]["password_hash"] = new_password_hash
    
    return True, "Password updated successfully"

def delete_user(users_data, username):
    
    if username not in users_data:
        return False, "User not found"
    
    
    del users_data[username]
    
    return True, "User deleted successfully"

def user_exists(username):
    users = load_users()
    return username in users

def email_exists(email):
    users = load_users()
    return any(user.get('email') == email for user in users.values())

def create_user(username, email, password):
    users = load_users()
    if username in users or any(user.get('email') == email for user in users.values()):
        return False
    
    users[username] = {
        'password_hash': generate_password_hash(password),
        'email': email,
        'created_at': datetime.now().isoformat()
    }
    save_users(users)
    return True
