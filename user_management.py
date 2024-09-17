# src/user_management.py

import json
from typing import List, Dict

# Reusing the USER_DB_PATH from auth.py
USER_DB_PATH = "user_database.json"

def load_user_database() -> List[Dict]:
    with open(USER_DB_PATH, 'r') as f:
        return json.load(f)

def save_user_database(users: List[Dict]):
    with open(USER_DB_PATH, 'w') as f:
        json.dump(users, f, indent=2)

def manage_users() -> List[Dict]:
    return load_user_database()

def search_user(search_term):
    users = manage_users()  # Fetch users from wherever they're stored
    for user in users:
        # Check if the search term matches the username (name) field
        if user.get('username', '').lower() == search_term.lower():
            return user  # Return the user dictionary if a match is found
    return None  # Return None if no match is found


def update_user(user_data: Dict) -> bool:
    users = load_user_database()  # Load the current users from the JSON file
    for i, user in enumerate(users):
        if user['username'] == user_data['username']:
            # Update only the fields present in user_data, keeping others unchanged
            users[i].update(user_data)
            save_user_database(users)  # Save the updated list back to the JSON file
            print(f"User {user_data['username']} updated in the JSON file.")  # Debugging output
            return True
    return False



def delete_user(username: str) -> bool:
    users = load_user_database()
    for i, user in enumerate(users):
        if user['username'] == username:
            del users[i]
            save_user_database(users)
            return True
    return False

def get_new_users() -> List[Dict]:
    users = load_user_database()
    return [user for user in users if user['role'] == 'new']

def approve_new_user(username: str, new_role: str) -> bool:
    users = load_user_database()
    for user in users:
        if user['username'] == username and user['role'] == 'new':
            user['role'] = new_role
            save_user_database(users)
            return True
    return False