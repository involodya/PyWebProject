from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import IntegerField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
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
    submit = SubmitField('Submit')