from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Users
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