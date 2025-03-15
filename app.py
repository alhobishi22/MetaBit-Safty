from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, DateField, FileField
from wtforms.validators import DataRequired, Optional
import io
import xlsxwriter
from flask import send_file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///fraud_reports.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Add zip to Jinja2 globals
app.jinja_env.globals.update(zip=zip)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    reports = db.relationship('Report', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # scammer, debt
    debt_amount = db.Column(db.Float)
    debt_date = db.Column(db.Date)
    scammer_name = db.Column(db.Text)
    scammer_phone = db.Column(db.Text)
    wallet_address = db.Column(db.Text)
    network_type = db.Column(db.Text)
    paypal = db.Column(db.String(100))
    payer = db.Column(db.String(100))
    perfect_money = db.Column(db.String(100))
    alkremi_bank = db.Column(db.String(100))
    jeeb_wallet = db.Column(db.String(100))
    jawali_wallet = db.Column(db.String(100))
    cash_wallet = db.Column(db.String(100))
    one_cash = db.Column(db.String(100))
    description = db.Column(db.Text)
    media_files = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportForm(FlaskForm):
    type = SelectField('نوع البلاغ', choices=[('scammer', 'نصاب'), ('debt', 'مديونية')], validators=[DataRequired()])
    debt_amount = FloatField('قيمة المديونية', validators=[Optional()])
    debt_date = DateField('تاريخ المديونية', validators=[Optional()])
    scammer_name = StringField('اسم النصاب', validators=[DataRequired()])
    scammer_phone = StringField('رقم الهاتف', validators=[DataRequired()])
    wallet_address = StringField('عنوان المحفظة', validators=[Optional()])
    network_type = StringField('نوع الشبكة', validators=[Optional()])
    paypal = StringField('PayPal', validators=[Optional()])
    payer = StringField('Payer', validators=[Optional()])
    perfect_money = StringField('Perfect Money', validators=[Optional()])
    alkremi_bank = StringField('بنك الكريمي', validators=[Optional()])
    jeeb_wallet = StringField('محفظة جيب', validators=[Optional()])
    jawali_wallet = StringField('محفظة جوالي', validators=[Optional()])
    cash_wallet = StringField('محفظة كاش', validators=[Optional()])
    one_cash = StringField('ون كاش', validators=[Optional()])
    description = TextAreaField('الوصف', validators=[DataRequired()])
    media_files = FileField('الملفات المرفقة', validators=[Optional()])

@login_manager.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route('/')
def index():
    # إحصائيات النظام
    total_reports = Report.query.count()
    scammer_reports = Report.query.filter_by(type='scammer').count()
    debt_reports = Report.query.filter_by(type='debt').count()
    total_users = User.query.count()
    
    # آخر البلاغات
    latest_reports = Report.query.order_by(Report.created_at.desc()).limit(4).all()
    
    return render_template('index.html', 
                         total_reports=total_reports,
                         scammer_reports=scammer_reports,
                         debt_reports=debt_reports,
                         total_users=total_users,
                         latest_reports=latest_reports)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    type_filter = request.args.get('type', 'all')
    
    if query:
        if type_filter != 'all':
            reports = Report.query.filter(
                Report.type == type_filter,
                db.or_(
                    Report.scammer_phone.contains(query),
                    Report.scammer_name.contains(query),
                    Report.paypal.contains(query),
                    Report.payer.contains(query),
                    Report.perfect_money.contains(query),
                    Report.alkremi_bank.contains(query),
                    Report.jeeb_wallet.contains(query),
                    Report.jawali_wallet.contains(query),
                    Report.cash_wallet.contains(query),
                    Report.one_cash.contains(query)
                )
            ).order_by(Report.created_at.desc()).all()
        else:
            reports = Report.query.filter(
                db.or_(
                    Report.scammer_phone.contains(query),
                    Report.scammer_name.contains(query),
                    Report.paypal.contains(query),
                    Report.payer.contains(query),
                    Report.perfect_money.contains(query),
                    Report.alkremi_bank.contains(query),
                    Report.jeeb_wallet.contains(query),
                    Report.jawali_wallet.contains(query),
                    Report.cash_wallet.contains(query),
                    Report.one_cash.contains(query)
                )
            ).order_by(Report.created_at.desc()).all()
    else:
        reports = []
    
    # Count duplicates for phone numbers, payment methods, and other identifiers
    duplicates = {}
    
    # Get all reports from database to count duplicates
    all_reports = Report.query.all()
    
    # Count phone numbers
    for report in all_reports:
        if report.scammer_phone:
            phones = report.scammer_phone.split('|')
            for phone in phones:
                phone = phone.strip()
                if phone:
                    if phone in duplicates:
                        duplicates[phone] += 1
                    else:
                        duplicates[phone] = 1
        
        # Count scammer names
        if report.scammer_name:
            names = report.scammer_name.split('|')
            for name in names:
                name = name.strip()
                if name:
                    if name in duplicates:
                        duplicates[name] += 1
                    else:
                        duplicates[name] = 1
        
        # Count wallet addresses
        if report.wallet_address:
            wallets = report.wallet_address.split('|')
            for wallet in wallets:
                wallet = wallet.strip()
                if wallet:
                    if wallet in duplicates:
                        duplicates[wallet] += 1
                    else:
                        duplicates[wallet] = 1
        
        # Count other identifiers (PayPal, bank accounts, etc.)
        for field in ['paypal', 'payer', 'perfect_money', 'alkremi_bank', 
                     'jeeb_wallet', 'jawali_wallet', 'cash_wallet', 'one_cash']:
            value = getattr(report, field)
            if value:
                if value in duplicates:
                    duplicates[value] += 1
                else:
                    duplicates[value] = 1
    
    return render_template('search.html', reports=reports, query=query, type_filter=type_filter, duplicates=duplicates)

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    if not current_user.is_authenticated:
        flash('يجب تسجيل الدخول لإضافة بلاغ جديد', 'warning')
        return redirect(url_for('login', next=request.path))

    form = ReportForm()
    if request.method == 'POST':
        # جمع البيانات من النموذج
        report_type = request.form.get('type')
        debt_amount = request.form.get('debt_amount')
        debt_date = request.form.get('debt_date')
        
        # جمع الأسماء المتعددة
        scammer_names = request.form.getlist('scammer_name')
        scammer_name = '|'.join(filter(None, scammer_names))
        
        # جمع أرقام الهواتف المتعددة
        scammer_phones = request.form.getlist('scammer_phone')
        scammer_phone = '|'.join(filter(None, scammer_phones))
        
        # جمع عناوين المحافظ وأنواع الشبكات
        wallet_addresses = request.form.getlist('wallet_address')
        network_types = request.form.getlist('network_type')
        wallet_address = '|'.join(filter(None, wallet_addresses))
        network_type = '|'.join(filter(None, network_types))

        # التحقق من صحة البيانات
        if not scammer_name:
            flash('يجب إدخال اسم النصاب', 'danger')
            return render_template('report.html', form=form)
        
        if not scammer_phone:
            flash('يجب إدخال رقم هاتف النصاب', 'danger')
            return render_template('report.html', form=form)
        
        if not report_type:
            flash('يجب اختيار نوع البلاغ', 'danger')
            return render_template('report.html', form=form)
        
        # التحقق من حقول المديونية فقط إذا كان نوع البلاغ "مدين"
        if report_type == 'debt':
            if not debt_amount:
                flash('يجب إدخال قيمة المديونية', 'danger')
                return render_template('report.html', form=form)
            if not debt_date:
                flash('يجب إدخال تاريخ المديونية', 'danger')
                return render_template('report.html', form=form)

        try:
            # إنشاء تقرير جديد
            report = Report(
                user_id=current_user.id,
                type=report_type,
                debt_amount=float(debt_amount) if debt_amount else None,
                debt_date=datetime.strptime(debt_date, '%Y-%m-%d').date() if debt_date else None,
                scammer_name=scammer_name,
                scammer_phone=scammer_phone,
                wallet_address=wallet_address,
                network_type=network_type,
                paypal=request.form.get('paypal'),
                payer=request.form.get('payer'),
                perfect_money=request.form.get('perfect_money'),
                alkremi_bank=request.form.get('alkremi_bank'),
                jeeb_wallet=request.form.get('jeeb_wallet'),
                jawali_wallet=request.form.get('jawali_wallet'),
                cash_wallet=request.form.get('cash_wallet'),
                one_cash=request.form.get('one_cash'),
                description=request.form.get('description')
            )

            # معالجة الملفات المرفقة
            media_files = []
            if 'media_files' in request.files:
                files = request.files.getlist('media_files')
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        media_files.append(filename)
            
            if media_files:
                report.media_files = ','.join(media_files)

            # حفظ التقرير في قاعدة البيانات
            db.session.add(report)
            db.session.commit()

            flash('تم إضافة البلاغ بنجاح', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء حفظ البلاغ. الرجاء المحاولة مرة أخرى.', 'danger')
            return render_template('report.html', form=form)

    return render_template('report.html', form=form)

@app.route('/edit_report/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_report(id):
    report = db.session.get(Report, id)
    if not report:
        abort(404)
    if report.user_id != current_user.id:
        abort(403)

    form = ReportForm(obj=report)
    if request.method == 'POST':
        # جمع البيانات من النموذج
        report_type = request.form.get('type')
        debt_amount = request.form.get('debt_amount')
        debt_date = request.form.get('debt_date')
        
        # جمع الأسماء المتعددة
        scammer_names = request.form.getlist('scammer_name')
        scammer_name = '|'.join(filter(None, scammer_names))
        
        # جمع أرقام الهواتف المتعددة
        scammer_phones = request.form.getlist('scammer_phone')
        scammer_phone = '|'.join(filter(None, scammer_phones))
        
        # جمع عناوين المحافظ وأنواع الشبكات
        wallet_addresses = request.form.getlist('wallet_address')
        network_types = request.form.getlist('network_type')
        wallet_address = '|'.join(filter(None, wallet_addresses))
        network_type = '|'.join(filter(None, network_types))

        # التحقق من صحة البيانات
        if not scammer_name:
            flash('يجب إدخال اسم النصاب', 'danger')
            return render_template('report.html', form=form, report=report)
        
        if not scammer_phone:
            flash('يجب إدخال رقم هاتف النصاب', 'danger')
            return render_template('report.html', form=form, report=report)
        
        if not report_type:
            flash('يجب اختيار نوع البلاغ', 'danger')
            return render_template('report.html', form=form, report=report)
        
        if report_type == 'debt':
            if not debt_amount:
                flash('يجب إدخال قيمة المديونية', 'danger')
                return render_template('report.html', form=form, report=report)
            if not debt_date:
                flash('يجب إدخال تاريخ المديونية', 'danger')
                return render_template('report.html', form=form, report=report)

        # تحديث البيانات
        report.type = report_type
        report.debt_amount = float(debt_amount) if debt_amount else None
        report.debt_date = datetime.strptime(debt_date, '%Y-%m-%d').date() if debt_date else None
        report.scammer_name = scammer_name
        report.scammer_phone = scammer_phone
        report.wallet_address = wallet_address
        report.network_type = network_type
        report.paypal = request.form.get('paypal')
        report.payer = request.form.get('payer')
        report.perfect_money = request.form.get('perfect_money')
        report.alkremi_bank = request.form.get('alkremi_bank')
        report.jeeb_wallet = request.form.get('jeeb_wallet')
        report.jawali_wallet = request.form.get('jawali_wallet')
        report.cash_wallet = request.form.get('cash_wallet')
        report.one_cash = request.form.get('one_cash')
        report.description = request.form.get('description')

        # معالجة الملفات المرفقة
        if 'media_files' in request.files:
            files = request.files.getlist('media_files')
            new_files = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    new_files.append(filename)
            
            if new_files:
                current_files = report.media_files.split(',') if report.media_files else []
                current_files.extend(new_files)
                report.media_files = ','.join(filter(None, current_files))

        db.session.commit()
        flash('تم تحديث البلاغ بنجاح', 'success')
        return redirect(url_for('view_report', id=report.id))

    return render_template('report.html', form=form, report=report)

@app.route('/report/<int:id>/delete', methods=['POST'])
@login_required
def delete_report(id):
    report = db.session.get(Report, id)
    if not report:
        abort(404)
    if report.user_id != current_user.id:
        flash('لا يمكنك حذف هذا البلاغ', 'danger')
        return redirect(url_for('index'))

    # حذف الملفات المرفقة
    if report.media_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], report.media_files)
        try:
            os.remove(file_path)
        except OSError:
            pass

    db.session.delete(report)
    db.session.commit()
    flash('تم حذف البلاغ بنجاح', 'success')
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('خطأ في اسم المستخدم أو كلمة المرور', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('تم إنشاء الحساب بنجاح', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))

@app.route('/view_report/<int:id>')
def view_report(id):
    report = db.session.get(Report, id)
    if not report:
        abort(404)
    
    # Count duplicates across all reports
    duplicates = {}
    all_reports = Report.query.all()
    
    # Process phone numbers
    for r in all_reports:
        if r.scammer_phone:
            phones = r.scammer_phone.split('|')
            for phone in phones:
                if phone.strip():
                    duplicates[phone.strip()] = duplicates.get(phone.strip(), 0) + 1
    
    # Process names
    for r in all_reports:
        if r.scammer_name:
            names = r.scammer_name.split('|')
            for name in names:
                if name.strip():
                    duplicates[name.strip()] = duplicates.get(name.strip(), 0) + 1
    
    # Process wallet addresses
    for r in all_reports:
        if r.wallet_address:
            addresses = r.wallet_address.split('|')
            for addr in addresses:
                if addr.strip():
                    duplicates[addr.strip()] = duplicates.get(addr.strip(), 0) + 1
    
    # Process payment methods
    payment_fields = ['paypal', 'payer', 'perfect_money', 'alkremi_bank', 
                     'jeeb_wallet', 'jawali_wallet', 'cash_wallet', 'one_cash']
    
    for r in all_reports:
        for field in payment_fields:
            value = getattr(r, field)
            if value:
                duplicates[value] = duplicates.get(value, 0) + 1
    
    return render_template('view_report.html', report=report, duplicates=duplicates)

@app.route('/get_all_contacts')
def get_all_contacts():
    # Get all reports from the database
    reports = Report.query.all()
    
    # Prepare data for JSON response
    contacts_data = []
    for report in reports:
        if report.scammer_phone:
            phones = report.scammer_phone.split('|')
            names = report.scammer_name.split('|') if report.scammer_name else []
            
            # Match phones with names
            for i, phone in enumerate(phones):
                if phone.strip():
                    name = names[i].strip() if i < len(names) and names[i].strip() else f"نصاب {len(contacts_data) + 1}"
                    contacts_data.append({
                        'name': name,
                        'phone': phone.strip()
                    })
    
    return jsonify(contacts_data)

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    # إحصائيات النظام
    total_reports = Report.query.count()
    scammer_reports = Report.query.filter_by(type='scammer').count()
    debt_reports = Report.query.filter_by(type='debt').count()
    total_users = User.query.count()
    
    return render_template('admin/dashboard.html', 
                         total_reports=total_reports,
                         scammer_reports=scammer_reports,
                         debt_reports=debt_reports,
                         total_users=total_users)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:id>/toggle_admin', methods=['POST'])
@login_required
def toggle_admin(id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    user = db.session.get(User, id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin_users'))
    
    # لا يمكن إلغاء صلاحيات المشرف الحالي
    if user.id == current_user.id:
        flash('لا يمكنك إلغاء صلاحيات المشرف الخاصة بك', 'warning')
        return redirect(url_for('admin_users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'منح' if user.is_admin else 'إلغاء'
    flash(f'تم {status} صلاحيات المشرف للمستخدم {user.username} بنجاح', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    user = db.session.get(User, id)
    if not user:
        flash('المستخدم غير موجود', 'danger')
        return redirect(url_for('admin_users'))
    
    # لا يمكن حذف المشرف الحالي
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'warning')
        return redirect(url_for('admin_users'))
    
    # حذف جميع البلاغات المرتبطة بالمستخدم
    reports = Report.query.filter_by(user_id=user.id).all()
    for report in reports:
        # حذف الملفات المرفقة
        if report.media_files:
            for filename in report.media_files.split(','):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        db.session.delete(report)
    
    # حذف المستخدم
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'تم حذف المستخدم {username} وجميع البلاغات المرتبطة به بنجاح', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    # فلترة البلاغات
    report_type = request.args.get('type', 'all')
    if report_type == 'scammer':
        reports = Report.query.filter_by(type='scammer').order_by(Report.created_at.desc()).all()
    elif report_type == 'debt':
        reports = Report.query.filter_by(type='debt').order_by(Report.created_at.desc()).all()
    else:
        reports = Report.query.order_by(Report.created_at.desc()).all()
    
    return render_template('admin/reports.html', reports=reports, report_type=report_type)

@app.route('/admin/reports/<int:id>/delete', methods=['POST'])
@login_required
def admin_delete_report(id):
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    report = db.session.get(Report, id)
    if not report:
        flash('البلاغ غير موجود', 'danger')
        return redirect(url_for('admin_reports'))
    
    # حذف الملفات المرفقة
    if report.media_files:
        for filename in report.media_files.split(','):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                os.remove(file_path)
            except OSError:
                pass
    
    db.session.delete(report)
    db.session.commit()
    
    flash('تم حذف البلاغ بنجاح', 'success')
    return redirect(url_for('admin_reports'))

@app.route('/admin/reports/export', methods=['GET'])
@login_required
def export_reports_excel():
    if not current_user.is_admin:
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('index'))
    
    # فلترة البلاغات
    report_type = request.args.get('type', 'all')
    if report_type == 'scammer':
        reports = Report.query.filter_by(type='scammer').order_by(Report.created_at.desc()).all()
        filename = "scammer_reports.xlsx"
    elif report_type == 'debt':
        reports = Report.query.filter_by(type='debt').order_by(Report.created_at.desc()).all()
        filename = "debt_reports.xlsx"
    else:
        reports = Report.query.order_by(Report.created_at.desc()).all()
        filename = "all_reports.xlsx"
    
    # إنشاء ملف إكسل في الذاكرة
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('البلاغات')
    
    # تنسيق العناوين
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#0d6efd',
        'color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })
    
    # تنسيق الخلايا
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })
    
    # تنسيق للنصابين
    scammer_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#ffcccc',
        'text_wrap': True
    })
    
    # تنسيق للمديونية
    debt_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#ffffcc',
        'text_wrap': True
    })
    
    # إعداد العناوين
    headers = [
        'رقم البلاغ', 'النوع', 'اسم النصاب', 'رقم الهاتف', 'المحفظة', 'الشبكة',
        'PayPal', 'Payer', 'Perfect Money', 'بنك الكريمي', 'محفظة جيب',
        'محفظة جوالي', 'محفظة كاش', 'ون كاش', 'قيمة المديونية', 'تاريخ المديونية',
        'الوصف', 'المستخدم', 'تاريخ الإنشاء'
    ]
    
    # كتابة العناوين
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # ضبط عرض الأعمدة
    worksheet.set_column(0, 0, 10)  # رقم البلاغ
    worksheet.set_column(1, 1, 15)  # النوع
    worksheet.set_column(2, 2, 25)  # اسم النصاب
    worksheet.set_column(3, 3, 20)  # رقم الهاتف
    worksheet.set_column(4, 14, 20)  # المحافظ والحسابات
    worksheet.set_column(15, 15, 15)  # تاريخ المديونية
    worksheet.set_column(16, 16, 40)  # الوصف
    worksheet.set_column(17, 17, 15)  # المستخدم
    worksheet.set_column(18, 18, 20)  # تاريخ الإنشاء
    
    # كتابة البيانات
    for row, report in enumerate(reports, start=1):
        # تحديد التنسيق بناءً على نوع البلاغ
        format_to_use = scammer_format if report.type == 'scammer' else debt_format
        
        # تحضير البيانات
        user = User.query.get(report.user_id)
        username = user.username if user else "غير معروف"
        
        # تقسيم البيانات المتعددة
        scammer_names = report.scammer_name.split('|') if report.scammer_name else []
        scammer_name = scammer_names[0] if scammer_names else ""
        
        scammer_phones = report.scammer_phone.split('|') if report.scammer_phone else []
        scammer_phone = scammer_phones[0] if scammer_phones else ""
        
        wallet_addresses = report.wallet_address.split('|') if report.wallet_address else []
        wallet_address = wallet_addresses[0] if wallet_addresses else ""
        
        network_types = report.network_type.split('|') if report.network_type else []
        network_type = network_types[0] if network_types else ""
        
        # تنسيق التواريخ
        created_at = report.created_at.strftime('%Y-%m-%d %H:%M') if report.created_at else ""
        debt_date = report.debt_date.strftime('%Y-%m-%d') if report.debt_date else ""
        
        # كتابة البيانات في الصفوف
        data = [
            report.id,
            'نصاب' if report.type == 'scammer' else 'مديونية',
            scammer_name,
            scammer_phone,
            wallet_address,
            network_type,
            report.paypal or "",
            report.payer or "",
            report.perfect_money or "",
            report.alkremi_bank or "",
            report.jeeb_wallet or "",
            report.jawali_wallet or "",
            report.cash_wallet or "",
            report.one_cash or "",
            report.debt_amount or "",
            debt_date,
            report.description or "",
            username,
            created_at
        ]
        
        for col, value in enumerate(data):
            worksheet.write(row, col, value, format_to_use)
    
    workbook.close()
    
    # إعادة مؤشر الملف إلى البداية
    output.seek(0)
    
    # إرسال الملف للتنزيل
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
