from flask import Blueprint, render_template, redirect, url_for, request, flash, session, make_response
from flask_wtf.csrf import generate_csrf

from .forms import RegistrationForm, LoginForm, ResetPasswordForm
from .models import User

from . import db
from .task_manager import login_required

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            response = make_response(redirect(url_for('auth.dashboard')))
            csrf_token = generate_csrf()
            response.set_cookie('csrf_token', csrf_token)
            return response
        else:
            flash('Неправильный email или пароль', 'danger')
    return render_template('login.html', form=form)


# Защита маршрутов
@auth.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('views.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Проверяем, есть ли пользователь с таким email в базе
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(request.url)

        # Создаем нового пользователя
        new_user = User(email=email, password=password, username=username)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth.route('/account', endpoint='account')
@login_required
def account():
    user = User.query.get(session.get('user_id'))
    return render_template('account.html', user=user)


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # НАСТРОИТЬ SMTP-отправку писем для восстановления пароля
        # НЕ ЗАБЫТЬ сменить ключи рекапчи на проде

        flash('Инструкции по сбросу пароля были отправлены на ваш адрес электронной почты.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)