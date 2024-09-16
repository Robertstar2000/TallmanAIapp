# src/auth.py

import json
import os
from typing import Dict, List, Tuple

# Path to the user database file
USER_DB_PATH = "user_database.json"

def load_user_database() -> List[Dict]:
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as f:
            return json.load(f)
    return []

def save_user_database(users: List[Dict]):
    with open(USER_DB_PATH, 'w') as f:
        json.dump(users, f, indent=2)

def authenticate_user(username: str, pin: str) -> dict:
    users = load_user_database()
    for user in users:
        if ('username' in user and user['username'] == username) or ('name' in user and user['name'] == username):
            if str(user['pin']) == str(pin):  # Ensure pins match
                if user['role'] != 'new':  # Ensure the user is not 'new'
                    return {"authenticated": True, "role": user['role']}  # Return user role for further checks
                else:
                    return {"authenticated": False, "message": f"User {username} is marked as 'new'"}
            else:
                return {"authenticated": False, "message": "PIN mismatch"}
    return {"authenticated": False, "message": "No matching user found"}



def create_new_account(username: str, pin: str, email: str) -> bool:
    users = load_user_database()
    
    # Check if username already exists
    if any(user['username'] == username for user in users):
        return False
    
    new_user = {
        'username': username,
        'pin': pin,
        'email': email,
        'role': 'new'
    }
    
    users.append(new_user)
    save_user_database(users)
    return True

def get_user_role(username: str) -> str:
    users = load_user_database()
    for user in users:
        if user['username'] == username:
            return user['role']
    return ''

# Initialize the user database with an admin user if it doesn't exist
if not os.path.exists(USER_DB_PATH):
    initial_users = [
        {
            'username': 'admin',
            'pin': '1234',
            'email': 'admin@tallmanequipment.com',
            'role': 'admin'
        }
    ]
    save_user_database(initial_users)