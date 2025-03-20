from app import app, db, User
from werkzeug.security import generate_password_hash

def setup_database():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        # Create a test user
        test_user = User(
            username='admin',
            email='alhubaishi@metabit.com'
        )
        test_user.set_password('admin123')
        
        # Add the test user to the database
        db.session.add(test_user)
        db.session.commit()

if __name__ == '__main__':
    setup_database()
    print("Database created successfully!")
