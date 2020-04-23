from flask import Flask, render_template, url_for, redirect
from data import db_session
from data.users import User
from forms import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
def main_page():
    return render_template('home.html', title='Коронавирус', css=url_for('static', filename='css/home_style.css'))


@app.route('/join', methods=['GET', 'POST'])
def join():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            email=form.email.data,
            about=form.about.data,
            education=form.education.data,
            speciality=form.speciality.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('join.html', title='Регистрация', form=form, css=url_for('static', filename='css/join_style.css'))


@app.route('/login')
def login():
    return 'dddd'


if __name__ == '__main__':
    main()
