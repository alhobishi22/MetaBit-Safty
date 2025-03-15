from app import app, db, User
from sqlalchemy import text

def update_database():
    with app.app_context():
        # Add the is_admin column to the user table
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            conn.commit()
        print("تم تحديث قاعدة البيانات بنجاح وإضافة حقل is_admin")
        
        # يمكنك ترقية مستخدم ليصبح مشرفًا هنا
        # على سبيل المثال، ترقية المستخدم الأول
        first_user = User.query.first()
        if first_user:
            first_user.is_admin = True
            db.session.commit()
            print(f"تم ترقية المستخدم '{first_user.username}' ليصبح مشرفًا")
        else:
            print("لم يتم العثور على أي مستخدمين في قاعدة البيانات")

if __name__ == "__main__":
    update_database()
