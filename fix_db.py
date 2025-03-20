#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
هذا الملف يقوم بإصلاح قاعدة البيانات في بيئة الإنتاج
بدلاً من إعادة تهيئتها، مما يحافظ على البيانات الموجودة
"""

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# استيراد التطبيق
try:
    from app import app, db
    print("تم استيراد التطبيق بنجاح")
except ImportError as e:
    print(f"خطأ في استيراد التطبيق: {e}")
    sys.exit(1)

def fix_database():
    """
    إصلاح قاعدة البيانات بدلاً من إعادة تهيئتها
    """
    try:
        with app.app_context():
            # التحقق من اتصال قاعدة البيانات
            db.engine.connect()
            print("تم الاتصال بقاعدة البيانات بنجاح")
            
            # التحقق من وجود الجداول وإنشائها إذا لم تكن موجودة
            db.create_all()
            print("تم التحقق من هيكل قاعدة البيانات")
            
            return True
    except Exception as e:
        print(f"خطأ في إصلاح قاعدة البيانات: {e}")
        return False

if __name__ == "__main__":
    print("بدء إصلاح قاعدة البيانات...")
    success = fix_database()
    
    if success:
        print("تم إصلاح قاعدة البيانات بنجاح")
        sys.exit(0)
    else:
        print("فشل في إصلاح قاعدة البيانات")
        sys.exit(1)
