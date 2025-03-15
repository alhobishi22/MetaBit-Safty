from app import app, db, User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        
        if admin:
            print(f"Admin user already exists: {admin.username}")
            print(f"Admin status: {'Yes' if admin.is_admin else 'No'}")
            
            # Make sure the user is an admin
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print("Updated user to admin status")
            
            # Reset admin password
            admin.password_hash = generate_password_hash('admin123')
            db.session.commit()
            print("Reset admin password to 'admin123'")
        else:
            # Create new admin user
            new_admin = User(
                username='admin',
                email='admin@metabit-safety.com',
                is_admin=True
            )
            new_admin.password_hash = generate_password_hash('admin123')
            
            db.session.add(new_admin)
            db.session.commit()
            print("Created new admin user:")
            print(f"Username: admin")
            print(f"Password: admin123")
            print(f"Email: admin@metabit-safety.com")

if __name__ == "__main__":
    create_admin()
