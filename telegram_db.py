import os
import string
import random
import re
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create a minimal Flask app for database context
app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///fraud_reports.db')
# تعديل رابط PostgreSQL إذا كان يبدأ بـ postgres:// (تغييره إلى postgresql://)
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف النماذج
class TelegramCode(db.Model):
    __tablename__ = 'telegram_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # العلاقة مع المستخدمين المسجلين
    registered_user = db.relationship('TelegramUser', backref='code_ref', uselist=False)

class TelegramUser(db.Model):
    __tablename__ = 'telegram_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(100))
    code_id = db.Column(db.Integer, db.ForeignKey('telegram_codes.id'))
    registered_at = db.Column(db.DateTime, server_default=db.func.now())

# Function to generate a random code
def generate_random_code(length=8, include_arabic=True):
    """Generate a random alphanumeric code with optional Arabic characters"""
    # English alphanumeric characters
    english_chars = string.ascii_letters + string.digits
    
    if include_arabic:
        # Arabic characters (basic set)
        arabic_chars = 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي'
        # Combined character set
        all_chars = english_chars + arabic_chars
    else:
        all_chars = english_chars
    
    # Generate a code with the selected character set
    return ''.join(random.choice(all_chars) for _ in range(length))

# Clean and normalize code for comparison
def normalize_code(code):
    # Remove whitespace and normalize
    return re.sub(r'\s+', '', code).strip().lower()

# Function to get all registration codes
def get_all_codes():
    codes_with_users = db.session.query(
        TelegramCode, TelegramUser
    ).outerjoin(
        TelegramUser, TelegramCode.id == TelegramUser.code_id
    ).order_by(
        TelegramCode.created_at.desc()
    ).all()
    
    result = []
    for code, user in codes_with_users:
        code_data = {
            'id': code.id,
            'code': code.code,
            'is_used': code.is_used,
            'created_at': code.created_at,
            'user_id': user.user_id if user else None,
            'username': user.username if user else None,
            'registered_at': user.registered_at if user else None
        }
        result.append(code_data)
    
    return result

# Function to get all registered users
def get_registered_users():
    users = TelegramUser.query.order_by(TelegramUser.registered_at.desc()).all()
    return users

# Verify registration code
def verify_code(code):
    if not code:
        return False
        
    normalized_code = normalize_code(code)
    
    # Get all unused codes
    unused_codes = TelegramCode.query.filter_by(is_used=False).all()
    
    # Check if the normalized input matches any normalized code
    for db_code in unused_codes:
        if normalized_code == normalize_code(db_code.code):
            return db_code.code  # Return the actual code from DB
    
    return None

# Mark code as used
def mark_code_used(code, user_id, username):
    # Find the code in the database
    telegram_code = TelegramCode.query.filter_by(code=code).first()
    if telegram_code:
        # Mark the code as used
        telegram_code.is_used = True
        
        # Create a new user registration
        new_user = TelegramUser(
            user_id=user_id,
            username=username,
            code_id=telegram_code.id
        )
        
        db.session.add(new_user)
        db.session.commit()
        return True
    return False

# Check if user is registered
def is_user_registered(user_id):
    user = TelegramUser.query.filter_by(user_id=user_id).first()
    return user is not None

# Get all registered users IDs
def get_all_registered_user_ids():
    users = TelegramUser.query.all()
    return [user.user_id for user in users]

# Create tables if they don't exist
def create_tables():
    with app.app_context():
        db.create_all()
        logger.info("Database tables created (if they didn't exist)")

# Initialize database
if __name__ == "__main__":
    create_tables()
