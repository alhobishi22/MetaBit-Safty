from app import app, db
import os

# تكوين التطبيق للنشر
# تعطيل وضع التصحيح في بيئة الإنتاج
app.config['DEBUG'] = False

# تهيئة قاعدة البيانات عند بدء التشغيل
with app.app_context():
    try:
        db.create_all()
        print("تم إنشاء جداول قاعدة البيانات بنجاح")
    except Exception as e:
        print(f"خطأ في إنشاء قاعدة البيانات: {str(e)}")

# تحديد المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
