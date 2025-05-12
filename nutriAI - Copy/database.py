from pymongo import MongoClient
import bcrypt
from config import MONGO_URI, DB_NAME, USERS_COLLECTION

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.users = self.db[USERS_COLLECTION]
        
        # Create unique index on email
        self.users.create_index("email", unique=True)

    def register_user(self, email: str, password: str, name: str):
        
        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user document
            user = {
                "email": email,
                "password": hashed_password,
                "name": name
            }
            
            # Insert user into database
            result = self.users.insert_one(user)
            return True, "Registration successful"
        except Exception as e:
            if "duplicate key error" in str(e):
                return False, "Email already exists"
            return False, str(e)

    def verify_user(self, email: str, password: str):
        try:
            # Find user by email
            user = self.users.find_one({"email": email})
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                return True, user
            return False, "Invalid email or password"
        except Exception as e:
            return False, str(e)

    def get_user_by_email(self, email: str):
        return self.users.find_one({"email": email})

# Initialize database
db = Database() 