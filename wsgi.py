from app import app
import os

# تكوين التطبيق للنشر
# تعطيل وضع التصحيح في بيئة الإنتاج
app.config['DEBUG'] = False

# تحديد المنفذ من متغيرات البيئة أو استخدام القيمة الافتراضية
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
