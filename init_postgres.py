from app import app, db, User
from werkzeug.security import generate_password_hash
from flask_migrate import upgrade

def init_postgres_db():
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # التحقق من وجود مستخدم مشرف
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # إنشاء مستخدم مشرف جديد
            new_admin = User(
                username='admin',
                email='admin@metabit-safety.com',
                is_admin=True
            )
            new_admin.password_hash = generate_password_hash('admin123')
            
            db.session.add(new_admin)
            db.session.commit()
            print("تم إنشاء مستخدم مشرف جديد:")
            print("اسم المستخدم: admin")
            print("كلمة المرور: admin123")
            print("البريد الإلكتروني: admin@metabit-safety.com")
        else:
            print("المستخدم المشرف موجود بالفعل")

if __name__ == "__main__":
    print("جاري تهيئة قاعدة بيانات PostgreSQL...")
    init_postgres_db()
    print("تم تهيئة قاعدة البيانات بنجاح!")
