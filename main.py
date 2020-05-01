from flask import Flask, render_template, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user
from data import db_session
from data.users import User
from data.regions import Region
from forms import RegisterForm, LoginForm, MakeQuestionForm
from random import shuffle
import sqlite3

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


def get_quiz_questions():
    con = sqlite3.connect("db/quiz_questions.db")
    cur = con.cursor()

    questions = cur.execute("""select * from questions""").fetchall()
    false_answers = cur.execute("""select question_id, false_answer from false_answers""").fetchall()
    ret = []

    for i in questions:
        ret.append(dict())
        ret[-1]['question'] = i[1]
        ret[-1]['right'] = i[2]
        ret[-1]['explanation'] = i[3]
        ret[-1]['false'] = []
        for j in false_answers:
            if j[0] == i[0]:
                ret[-1]['false'].append(j[1])

    con.commit()

    return ret


@app.route('/quiz/add_question', methods=['GET', 'POST'])
def add_question():
    form = MakeQuestionForm()
    if form.validate_on_submit():
        con = sqlite3.connect("db/quiz_questions.db")
        cur = con.cursor()
        s = f'insert into questions(question, right_answer, explanation) values("{form.question.data}", "{form.right_answer.data}", "{form.explanation.data}")'
        cur.execute(s)

        s = f'select id from questions where right_answer = "{form.right_answer.data}"'
        id = cur.execute(s).fetchall()[0][0]

        for false_answer in form.false_answers.data.split('\n'):
            false_answer = false_answer.strip(chr(13))
            s = """insert into false_answers(question_id, false_answer) values(""" + str(id) + ', ' + '\'' + false_answer + '\')'
            cur.execute(s)

        con.commit()

        return redirect('/')

    return render_template('quiz_add_question.html', form=form)


@app.route('/quiz/<question_number>/<status>', methods=['GET', 'POST'])
def quiz(question_number, status):
    questions = get_quiz_questions()

    if not question_number.isdigit():
        return redirect('/')
    question_number = int(question_number)

    if status == 'start':
        session['answer_list'] = [-1] * len(questions)
        return render_template('start_quiz.html', next_page='/quiz/0/question', answer_list=session['answer_list'])
    elif question_number >= len(questions):
        return render_template('quiz_end.html', answer_list=session['answer_list'])
    elif status == 'question':
        question = questions[question_number]['question']
        answers = [questions[question_number]['right'], *questions[question_number]['false']]
        shuffle(answers)
        return render_template('quiz_question.html', question=question, answers=answers,
                               next_page=f'/quiz/{question_number}', question_number=question_number,
                               answer_list=session['answer_list'])
    else:
        answer = status

        right = answer == questions[question_number]['right']
        if right:
            session['answer_list'][question_number] = 1
        else:
            session['answer_list'][question_number] = 0

        return render_template('quiz_explanation.html', right=right,
                               next_page=f'/quiz/{question_number + 1}/question',
                               explanation=questions[question_number]['explanation'] if 'explanation' in questions[
                                   question_number].keys() else '', right_answer=questions[question_number]['right'],
                               answer_list=session['answer_list'])



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
