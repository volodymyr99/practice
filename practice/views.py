from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Users, PracticeBases
from . import db


views = Blueprint('views', __name__)

@views.route('/')
#@views.route('/home')
def home():    
    return render_template(
        'index.html'
    )

@views.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@views.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = db.session.query(Users).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вхід успішний', category='success')
            return redirect(url_for('views.about'))
        else:
            flash('Невірний email або пароль', category='error')
    return render_template('login.html')


@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.login'))


@views.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)



@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        username = request.form.get('username', '').strip()
        role = request.form.get('role', 'student')  # За замовчуванням — студент

        # Перевірка, чи користувач з таким email вже існує
        existing_user = db.session.query(Users).filter_by(email=email).first()
        if existing_user:
            flash('Користувач з таким email вже існує.', 'error')
            return render_template('register.html')

        # Хешування пароля
        password_hash = generate_password_hash(password)

        # Створення нового користувача
        new_user = Users(
            email=email,
            password_hash=password_hash,
            role=role,
            username=username
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Реєстрація успішна! Тепер увійдіть у свій акаунт.', 'success')
        return redirect(url_for('views.login'))

    return render_template('register.html')

@views.route('/manage_practice_bases', methods=['GET', 'POST'])
@login_required
def manage_practice_bases():
    # Перевірка чи користувач має роль staff
    if current_user.role != 'staff':
        flash('У вас немає доступу до цієї сторінки', 'error')
        return redirect(url_for('views.home'))

    # Отримання ID для редагування або видалення з query параметрів
    edit_id = request.args.get('edit', type=int)
    delete_id = request.args.get('delete', type=int)

    if request.method == 'POST':
        if delete_id:
            # Видалення бази практики
            base = db.session.get(PracticeBases, delete_id)
            if base:
                db.session.delete(base)
                db.session.commit()
                flash('Базу практики успішно видалено', 'success')
            return redirect(url_for('views.manage_practice_bases'))

        # Отримання даних з форми
        name = request.form.get('name')
        address = request.form.get('address')
        contact_info = request.form.get('contact_info')
        base_id = request.form.get('base_id')

        if base_id:
            # Редагування існуючої бази практики
            base = db.session.get(PracticeBases, int(base_id))
            if base:
                base.name = name
                base.address = address
                base.contact_info = contact_info
                flash('Базу практики успішно оновлено', 'success')
        else:
            # Додавання нової бази практики
            new_base = PracticeBases(
                name=name,
                address=address,
                contact_info=contact_info
            )
            db.session.add(new_base)
            flash('Нову базу практики успішно додано', 'success')

        db.session.commit()
        return redirect(url_for('views.manage_practice_bases'))

    # Отримання бази практики для редагування
    base = None
    if edit_id:
        base = db.session.get(PracticeBases, edit_id)

    # Отримання всіх баз практики для відображення в таблиці
    practice_bases = db.session.query(PracticeBases).all()

    return render_template('manage_practice_bases.html', 
                         base=base,
                         practice_bases=practice_bases)