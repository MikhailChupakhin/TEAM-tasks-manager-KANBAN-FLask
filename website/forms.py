from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, Optional, InputRequired
from wtforms.fields.datetime import DateField


### Формы АУТЕНТИФИКАЦИИ

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=8, max=30, message="Имя пользователя должно быть от 8 до 30 символов")])
    password_validator = Regexp(regex=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,30}$',
                                message="Пароль должен содержать хотя бы одну цифру, одну строчную и одну прописную латинскую букву, и иметь от 8 до 30 символов")
    password = PasswordField('Пароль', validators=[DataRequired(), password_validator])
    password2 = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    email = StringField('Адрес электронной почты', validators=[DataRequired(), Email(message="Введите корректный адрес электронной почты")])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Адрес электронной почты', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    recaptcha = RecaptchaField()


### Формы ТАСК-МЕНЕДЖЕРА


class ProjectCreationForm(FlaskForm):
    name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание проекта')
    type = SelectField('Тип проекта', choices=[('basic', 'Простой'), ('devflow', 'DevFlow')],
                               validators=[DataRequired()])
    submit = SubmitField('Создать проект')


class InviteCreationForm(FlaskForm):
    recipient = StringField('Введите email пользователя', validators=[DataRequired()])
    role = SelectField('Роль участника', choices=['Teamlead', 'Vendor', 'Administrator', 'Tester'], default='basic')
    submit = SubmitField('Пригласить')


class RemoveMemberForm(FlaskForm):
    submit = SubmitField('Исключить участника')


class TaskCreationForm(FlaskForm):
    name = StringField('Название задачи', validators=[DataRequired()])
    description = TextAreaField('Описание задачи')
    deadline = DateField('Дэдлайн', format='%Y-%m-%d', validators=[Optional()])
    responsible = SelectField('Ответственный', coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField('Создать задачу')


class TaskEditForm(FlaskForm):
    name = StringField('Название задачи', validators=[DataRequired()])
    description = TextAreaField('Описание задачи')
    deadline = DateField('Дэдлайн', format='%Y-%m-%d', validators=[Optional()])
    responsible = SelectField('Ответственный', coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField('Сохранить изменения')