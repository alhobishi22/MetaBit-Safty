<<<<<<< HEAD
import os
import sys
import logging
from sqlalchemy import inspect, text
from app import app, db, User

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin():
    with app.app_context():
        try:
            # التحقق من نوع قاعدة البيانات
            logger.info(f"Database type: {db.engine.name}")
            
            # التحقق من الجداول الموجودة
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Existing tables: {existing_tables}")
            
            # التحقق من وجود جدول المستخدمين
            if 'users' not in existing_tables:
                logger.warning("Users table does not exist. Creating tables...")
                # إنشاء جميع الجداول
                db.create_all()
                
                # التحقق مرة أخرى
                existing_tables = inspector.get_table_names()
                logger.info(f"Tables after creation: {existing_tables}")
                
                if 'users' not in existing_tables:
                    logger.error("Failed to create users table!")
                    return False
            
            # إنشاء مستخدم مشرف
            logger.info("Creating admin user...")
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                # إنشاء مستخدم مشرف جديد
                new_admin = User(
                    username='metabit',
                    email='admin@metabit-safety.com',
                    is_admin=True
                )
                new_admin.set_password('Zx1537671++')
                
                db.session.add(new_admin)
                db.session.commit()
                logger.info("Admin user created successfully")
                logger.info("Username: admin")
                logger.info("Password: admin123")
                logger.info("Email: admin@metabit-safety.com")
            else:
                logger.info("Admin user already exists")
                # تحديث كلمة المرور للمستخدم المشرف الحالي
                admin.set_password('admin123')
                admin.is_admin = True
                admin.email = 'admin@metabit-safety.com'
                db.session.commit()
                logger.info("Admin user updated successfully")
                logger.info("Username: admin")
                logger.info("Password: admin123")
                logger.info("Email: admin@metabit-safety.com")
            
            return True
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
            import traceback
            traceback.print_exc(file=sys.stdout)
            return False

if __name__ == "__main__":
    logger.info("Starting admin user creation...")
    success = create_admin()
    if success:
        logger.info("Admin user creation completed successfully")
    else:
        logger.error("Admin user creation failed")
=======
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
            admin.set_password('admin123')
            db.session.commit()
            print("Reset admin password to 'admin123'")
        else:
            # Create new admin user
            new_admin = User(
                username='admin',
                email='admin@metabit-safety.com',
                is_admin=True
            )
            new_admin.set_password('admin123')
            
            db.session.add(new_admin)
            db.session.commit()
            print("Created new admin user:")
            print(f"Username: admin")
            print(f"Password: admin123")
            print(f"Email: admin@metabit-safety.com")

if __name__ == "__main__":
    create_admin()
>>>>>>> 0b2e9edf5d191e0912dd4d125ab7926541c65858
