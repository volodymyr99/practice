from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .models import Users, PracticeBases, Groups, PracticeStages, PracticeAssignments
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

@views.route('/manage_groups', methods=['GET', 'POST'])
@login_required
def manage_groups():
    # Перевірка чи користувач має роль staff
    if current_user.role != 'staff':
        flash('У вас немає доступу до цієї сторінки', 'error')
        return redirect(url_for('views.home'))

    # Отримання ID для редагування або видалення з query параметрів
    edit_id = request.args.get('edit', type=int)
    delete_id = request.args.get('delete', type=int)

    if request.method == 'POST':
        if delete_id:
            # Видалення групи
            group = db.session.get(Groups, delete_id)
            if group:
                db.session.delete(group)
                db.session.commit()
                flash('Групу успішно видалено', 'success')
            return redirect(url_for('views.manage_groups'))

        # Отримання даних з форми
        name = request.form.get('name')
        year = request.form.get('year')
        group_id = request.form.get('group_id')

        if group_id:
            # Редагування існуючої групи
            group = db.session.get(Groups, int(group_id))
            if group:
                group.name = name
                group.year = year
                flash('Групу успішно оновлено', 'success')
        else:
            # Додавання нової групи
            new_group = Groups(
                name=name,
                year=year
            )
            db.session.add(new_group)
            flash('Нову групу успішно додано', 'success')

        db.session.commit()
        return redirect(url_for('views.manage_groups'))

    # Отримання групи для редагування
    group = None
    if edit_id:
        group = db.session.get(Groups, edit_id)

    # Отримання всіх груп для відображення в таблиці
    groups = db.session.query(Groups).all()

    return render_template('manage_groups.html', 
                         group=group,
                         groups=groups)

@views.route('/manage_group_students/<int:group_id>', methods=['GET', 'POST'])
@login_required
def manage_group_students(group_id):
    # Перевірка чи користувач має роль staff
    if current_user.role != 'staff':
        flash('У вас немає доступу до цієї сторінки', 'error')
        return redirect(url_for('views.home'))

    # Отримання групи
    group = db.session.get(Groups, group_id)
    if not group:
        flash('Групу не знайдено', 'error')
        return redirect(url_for('views.manage_groups'))

    # Отримання ID студента для видалення з групи
    remove_student_id = request.args.get('remove', type=int)

    if request.method == 'POST':
        if remove_student_id:
            # Видалення студента з групи
            student = db.session.get(Users, remove_student_id)
            if student and student.group_id == group_id:
                student.group_id = None
                db.session.commit()
                flash('Студента успішно видалено з групи', 'success')
        else:
            # Додавання студента до групи
            student_id = request.form.get('student_id')
            student = db.session.get(Users, student_id)
            if student and student.role == 'student':
                student.group_id = group_id
                db.session.commit()
                flash('Студента успішно додано до групи', 'success')
            else:
                flash('Неможливо додати цього користувача до групи', 'error')

        return redirect(url_for('views.manage_group_students', group_id=group_id))

    # Отримання студентів групи
    group_students = db.session.query(Users).filter_by(group_id=group_id, role='student').all()

    # Отримання доступних студентів (які не в групі)
    available_students = db.session.query(Users).filter_by(role='student', group_id=None).all()

    return render_template('manage_group_students.html',
                         group=group,
                         group_students=group_students,
                         available_students=available_students)

@views.route('/create_practice_order', methods=['GET', 'POST'])
@login_required
def create_practice_order():
    # Перевірка чи користувач має роль staff
    if current_user.role != 'staff':
        flash('У вас немає доступу до цієї сторінки', 'error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        # Отримання даних з форми
        group_id = request.form.get('group_id')
        practice_stage_id = request.form.get('practice_stage_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Отримання групи та перевірка її існування
        group = db.session.get(Groups, group_id)
        if not group:
            flash('Групу не знайдено', 'error')
            return redirect(url_for('views.create_practice_order'))

        # Отримання студентів групи
        students = db.session.query(Users).filter_by(group_id=group_id, role='student').all()
        
        # Створення призначень практики для кожного студента
        assignments = []
        for student in students:
            base_id = request.form.get(f'base_id_{student.id}')
            supervisor_id = request.form.get(f'supervisor_id_{student.id}')

            if not base_id or not supervisor_id:
                flash('Не всі студенти мають призначені бази практики та керівників', 'error')
                return redirect(url_for('views.create_practice_order'))

            # Створення призначення практики
            assignment = PracticeAssignments(
                student_id=student.id,
                group_id=group_id,
                practice_stage_id=practice_stage_id,
                supervisor_id=supervisor_id,
                base_id=base_id,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                status='assigned'
            )
            db.session.add(assignment)
            assignments.append(assignment)

        db.session.commit()

        # Перенаправлення на сторінку з наказом
        return render_template('practice_order.html',
                             group=group,
                             start_date=start_date,
                             end_date=end_date,
                             assignments=assignments)

    # GET запит - відображення форми
    groups = db.session.query(Groups).all()
    practice_stages = db.session.query(PracticeStages).all()
    practice_bases = db.session.query(PracticeBases).all()
    teachers = db.session.query(Users).filter_by(role='teacher').all()

    return render_template('create_practice_order.html',
                         groups=groups,
                         practice_stages=practice_stages,
                         practice_bases=practice_bases,
                         teachers=teachers)

@views.route('/get_group_students/<int:group_id>')
@login_required
def get_group_students(group_id):
    try:
        if current_user.role != 'staff':
            return jsonify({'error': 'Unauthorized'}), 403

        # Перевіряємо існування групи
        group = db.session.get(Groups, group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404

        # Отримуємо студентів групи
        students = db.session.query(Users).filter_by(group_id=group_id, role='student').all()
        
        # Формуємо відповідь
        students_data = [{
            'id': student.id,
            'username': student.username,
            'full_name': student.full_name or student.username
        } for student in students]

        return jsonify({
            'success': True,
            'students': students_data
        })

    except Exception as e:
        print(f"Error in get_group_students: {str(e)}")  # Для дебагу
        return jsonify({'error': 'Internal server error'}), 500