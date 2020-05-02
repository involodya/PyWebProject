from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms import IntegerField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    """ форма регистрации """

    email = EmailField('E-mail:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль:', validators=[DataRequired()])
    surname = StringField('Фамилия:', validators=[DataRequired()])
    name = StringField('Имя:', validators=[DataRequired()])
    age = IntegerField('Возраст:', validators=[DataRequired()])
    about = StringField('О себе:')
    education = StringField('Образование:', validators=[DataRequired()])
    speciality = StringField('Род деятельности:', validators=[DataRequired()])
    agree = BooleanField('Согласен на обработку персональных данных:', validators=[DataRequired()])
    avatar = FileField('Загрузите фото профиля')
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    """ форма входа на сайт """

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class PostForm(FlaskForm):
    """ форма создания поста """

    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    attachment = FileField('Прикрепить фото')
    submit = SubmitField('Запостить')


class MakeQuestionForm(FlaskForm):
    """ форма создания вопроса для викторины """

    question = StringField('Вопрос', validators=[DataRequired()])
    right_answer = StringField('Правильный ответ', validators=[DataRequired()])
    false_answers = TextAreaField('Неправильныу ответы', validators=[DataRequired()])
    explanation = StringField('Пояснение')
    submit = SubmitField('Создать вопрос')
