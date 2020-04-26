from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from data import db_session
from data.users import User
from data.regions import Region
from forms import RegisterForm, LoginForm
from random import shuffle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)


@app.route('/')
def main_page():
    return render_template('home.html', title='Коронавирус', css=url_for('static', filename='css/home_style.css'))


@app.route('/regions')
def regions():
    """ Обработчик страницы со списком регионов """

    session = db_session.create_session()
    regions = session.query(Region).all()
    return render_template('regions.html', title='Регионы', regions=regions,
                           css=url_for('static', filename='css/regions_style.css'))


@app.route('/regions/<region_id>')
def region(region_id):
    """ Обработчик страницы региона """

    session = db_session.create_session()
    region = session.query(Region).filter(Region.id == region_id).first()
    return render_template('region.html', title=region.name, region=region,
                           css=url_for('static', filename='css/region_style.css'))


@app.route('/join', methods=['GET', 'POST'])
def join():
    """ обработчик регистрации пользователя """

    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('join.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают",
                                   css=url_for('static', filename='css/join_style.css'))
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('join.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   css=url_for('static', filename='css/join_style.css'))
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
    return render_template('join.html', title='Регистрация', form=form,
                           css=url_for('static', filename='css/join_style.css'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ обратчик страницы с авторизацией """

    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form,
                               css=url_for('static', filename='css/login_style.css'))
    return render_template('login.html', title='Авторизация', form=form,
                           css=url_for('static', filename='css/login_style.css'))


@app.route('/quiz/<question_number>/<status>', methods=['GET', 'POST'])
def quiz(question_number, status):
    questions = [
        {
            'question': 'Что такое коронавирус?',
            'right': 'Инфекционное заболевание, вызванное новым, ранее неизвестным коронавирусом',
            'false': 'Мутировавший свиной грип'
        },

        {
            'question': 'Как еще называют коронавирус',
            'right': 'COVID-19',
            'false': 'COVID-2018'
        },

        {
            'question': 'Как в основном передается коронавирус?',
            'right': 'В основном через капли, выделяющиеся из дыхательных путей при кашле, чихании и дыхании, а так-же через касания.',
            'false': 'Коронавирус разносят птицы и обитающие в городах крысы.',
        },

        {
            'question': 'Можно ли трогать руками лицо?',
            'right': 'Нет',
            'false': 'Да',
            'explanation': 'Лицо, а в особенности нос и глаза, лучше не трогать руками так как быстрее всего коронавирус попалает в организм через слизистую оболочку.'
        },

        {
            'question': 'Может ли вирус проникнуть через маску?',
            'right': 'Может.',
            'false': 'Не может.',
            'explanation': 'Вирус настолько мал, что может проникнать практически через все цели, в том числе и через щели в маске. Однако коронавирус передается в основном при чихании или кашле, то есть переносится он в капельках слюны, а их маска задержать может.'
        }]

    if not question_number.isdigit():
        return redirect('/')
    question_number = int(question_number)

    if status == 'start':
        return render_template('start_quiz.html', next_page='/quiz/1/question')
    elif question_number >= len(questions):
        return render_template('quiz_end.html')
    elif status == 'question':
        question = questions[question_number]['question']
        answers = [questions[question_number]['right'], questions[question_number]['false']]
        shuffle(answers)
        return render_template('quiz_question.html', question=question, answers=answers,
                               next_page=f'/quiz/{question_number}', question_number=question_number)
    else:
        answer = status
        return render_template('quiz_explanation.html', right=(answer == questions[question_number]['right']),
                               next_page=f'/quiz/{question_number + 1}/question',
                               explanation=questions[question_number]['explanation'] if 'explanation' in questions[
                                   question_number].keys() else '', right_answer=questions[question_number]['right'])


@login_manager.user_loader
def load_user(user_id):
    """ обработчик входа пользователя """

    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    """ обработчик выхода пользователя """

    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
