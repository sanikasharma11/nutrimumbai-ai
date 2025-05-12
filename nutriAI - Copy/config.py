import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DB_NAME = 'nutrimumbai'
USERS_COLLECTION = 'users'

# Security Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
COOKIE_NAME = 'nutrimumbai_auth'
COOKIE_KEY = 'nutrimumbai_key'

# Session Configuration
SESSION_EXPIRY_DAYS = 30 