import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json

class PasswordManager:
    def __init__(self, master_password):
        # Generate encryption key from master password
        salt = b'securesalt123456'  # In production, generate and store unique salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.cipher = Fernet(key)
        self.password_file = 'passwords.json'
        
    def save_password(self, website, username, password):
        """Encrypt and save a password"""
        passwords = self.load_passwords()
        
        # Encrypt the password
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        
        passwords[website] = {
            'username': username,
            'password': encrypted_password
        }
        
        # Save to file
        with open(self.password_file, 'w') as f:
            json.dump(passwords, f)
        
        return True
    
    def get_password(self, website):
        """Retrieve and decrypt a password"""
        passwords = self.load_passwords()
        
        if website not in passwords:
            return None
        
        entry = passwords[website]
        
        # Decrypt the password
        decrypted_password = self.cipher.decrypt(entry['password'].encode()).decode()
        
        return {
            'username': entry['username'],
            'password': decrypted_password
        }
    
    def load_passwords(self):
        """Load passwords from file or return empty dict if file doesn't exist"""
        try:
            with open(self.password_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def delete_password(self, website):
        """Delete a password entry"""
        passwords = self.load_passwords()
        
        if website in passwords:
            del passwords[website]
            
            # Save to file
            with open(self.password_file, 'w') as f:
                json.dump(passwords, f)
            
            return True
        
        return False