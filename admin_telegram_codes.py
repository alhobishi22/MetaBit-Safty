import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import csv
from io import StringIO
from flask import Response
from telegram_db import (
    app as telegram_app, 
    db, 
    TelegramCode, 
    TelegramUser, 
    generate_random_code, 
    get_all_codes, 
    get_registered_users
)

# Create a Blueprint for telegram code management
telegram_codes_bp = Blueprint('telegram_codes', __name__)

# Routes for telegram code management
@telegram_codes_bp.route('/admin/telegram-codes')
@login_required
def telegram_codes():
    if not current_user.is_admin:
        flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    with telegram_app.app_context():
        codes = get_all_codes()
        users = get_registered_users()
    
    return render_template('admin_telegram_codes.html', codes=codes, users=users)

@telegram_codes_bp.route('/admin/telegram-codes/generate', methods=['POST'])
@login_required
def generate_code():
    if not current_user.is_admin:
        flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    num_codes = int(request.form.get('num_codes', 1))
    code_length = int(request.form.get('code_length', 8))
    include_arabic = request.form.get('include_arabic') == 'on'
    
    with telegram_app.app_context():
        for _ in range(num_codes):
            # Generate a unique code
            while True:
                code_text = generate_random_code(code_length, include_arabic)
                existing_code = TelegramCode.query.filter_by(code=code_text).first()
                if not existing_code:
                    break
            
            # إنشاء كود جديد باستخدام SQLAlchemy
            new_code = TelegramCode(code=code_text)
            db.session.add(new_code)
        
        db.session.commit()
    
    flash(f'تم إنشاء {num_codes} كود تسجيل بنجاح', 'success')
    return redirect(url_for('telegram_codes.telegram_codes'))

@telegram_codes_bp.route('/admin/telegram-codes/delete/<int:code_id>', methods=['POST'])
@login_required
def delete_code(code_id):
    if not current_user.is_admin:
        flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    with telegram_app.app_context():
        # البحث عن الكود باستخدام SQLAlchemy
        code = TelegramCode.query.get(code_id)
        
        if code:
            # البحث عن المستخدم المرتبط بالكود
            user = TelegramUser.query.filter_by(code_id=code_id).first()
            
            # حذف المستخدم إذا وجد
            if user:
                db.session.delete(user)
            
            # حذف الكود
            db.session.delete(code)
            db.session.commit()
            
            flash('تم حذف كود التسجيل بنجاح', 'success')
        else:
            flash('لم يتم العثور على كود التسجيل', 'danger')
    
    return redirect(url_for('telegram_codes.telegram_codes'))

@telegram_codes_bp.route('/admin/telegram-codes/export', methods=['GET'])
@login_required
def export_codes():
    if not current_user.is_admin:
        flash('يجب أن تكون مسؤولاً للوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('index'))
    
    with telegram_app.app_context():
        codes = get_all_codes()
    
    # Create CSV file
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Code', 'Used', 'Created At', 'User ID', 'Username', 'Registered At'])
    
    for code in codes:
        cw.writerow([
            code['id'], 
            code['code'], 
            'Yes' if code['is_used'] else 'No', 
            code['created_at'],
            code['user_id'] if code['user_id'] else '',
            code['username'] if code['username'] else '',
            code['registered_at'] if code['registered_at'] else ''
        ])
    
    output = si.getvalue()
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=telegram_codes.csv"}
    )
