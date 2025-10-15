#!/usr/bin/env python3
"""
Test file to demonstrate AI code review functionality
"""

import os
import requests
from typing import List, Dict, Optional

class UserManager:
    def __init__(self):
        self.users = []
        self.db_connection = None
    
    def add_user(self, name: str, email: str, age: int = None):
        """Add a new user to the system"""
        # Adding some intentional issues for AI to catch
        if not name:
            raise ValueError("Name cannot be empty")
        
        user = {
            "name": name,
            "email": email,
            "age": age  # No validation for negative ages
        }
        self.users.append(user)
        return user
    
    def get_user_by_email(self, email: str):
        """Get user by email address"""
        for user in self.users:
            if user["email"] == email:  # Case sensitive comparison
                return user
        return None
    
    def delete_user(self, user_id: int):
        """Delete user by ID"""
        # Potential issue: no bounds checking
        if user_id < len(self.users):
            del self.users[user_id]
            return True
        return False
    
    def fetch_user_data(self, user_id: int):
        """Fetch user data from external API"""
        url = "https://api.example.com/users/{}".format(user_id)
        response = requests.get(url)  # No timeout, no error handling
        
        if response.status_code == 200:
            return response.json()
        else:
            return None

def process_users(user_list: List[str]):
    """Process a list of user names"""
    results = []
    
    for name in user_list:
        # String concatenation instead of f-strings
        processed_name = "User: " + name.upper()
        results.append(processed_name)
    
    return results

# Global variable - not ideal
current_user = None

def set_current_user(user):
    global current_user
    current_user = user

if __name__ == "__main__":
    manager = UserManager()
    
    # Add some test users
    manager.add_user("John Doe", "john@example.com", 30)
    manager.add_user("Jane Smith", "jane@example.com")
    
    # Test the functionality
    user = manager.get_user_by_email("john@example.com")
    print(f"Found user: {user}")
    
    # Process some names
    names = ["alice", "bob", "charlie"]
    processed = process_users(names)
    print(f"Processed names: {processed}")
