from flask import Flask, render_template, url_for, redirect, request, abort, session
import sqlite3
from data import db_session
from data.users import User
from data.regions import Region

from data.posts import Post
import datetime
import os

from PIL import Image
from data.posts import Post
from data.regions import Region
from data.users import User
from flask import Flask, render_template, url_for, redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms import RegisterForm, LoginForm, PostForm

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)


@app.route('/')
def main_page():
    """ обработчик главной страницы """

    return render_template('home.html', title='Коронавирус',
                           css=url_for('static', filename='css/home_style.css'))


@app.route("/blog")
def index():
    """ Обработчик страницы с блогом """

    session = db_session.create_session()
    posts = session.query(Post).all()
    posts = sorted(posts, key=lambda x: x.created_date, reverse=True)
    return render_template("blog.html", posts=posts, title='Блог',
                           css=url_for('static', filename='css/blog_style.css'))


@app.route('/post', methods=['GET', 'POST'])
@login_required
def add_post():
    """ Обработчик страницы создания поста """

    form = PostForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        post = Post()
        post.title = form.title.data
        post.content = form.content.data
        post.string_created_date = str(datetime.datetime.now())[0:16]
        current_user.posts.append(post)
        session.merge(current_user)
        session.commit()
        if bool(form.attachment.data):
            session = db_session.create_session()
            post = session.query(Post).order_by(Post.id.desc()).first()
            f = form.attachment.data
            type = f.filename.split('.')[-1]
            filename = f'post_attachment_{post.id}.{type}'
            path = os.path.join(
                'static', 'attachments', filename
            )
            f.save(path)
            post.attachment = path
            session.commit()
        return redirect('/blog')
    return render_template('post.html', title='Новый пост',
                           form=form, css=url_for('static', filename='css/post_style.css'))


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    """ Обработчик страницы редактирования поста """

    form = PostForm()
    if request.method == "GET":
        session = db_session.create_session()
        if current_user.role == 'admin':
            post = session.query(Post).filter(Post.id == id).first()
        else:
            post = session.query(Post).filter(Post.id == id,
                                              Post.user == current_user).first()
        if post:
            form.title.data = post.title
            form.content.data = post.content
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        if current_user.role == 'admin':
            post = session.query(Post).filter(Post.id == id).first()
        else:
            post = session.query(Post).filter(Post.id == id,
                                              Post.user == current_user).first()
        if post:
            post.title = form.title.data
            post.content = form.content.data
            session.commit()
            return redirect('/blog')
        else:
            abort(404)
    return render_template('post.html', title='Редактирование поста',
                           form=form, css=url_for('static', filename='css/post_style.css'))


@app.route('/post_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def post_delete(id):
    """ обработчик удаления поста """

    session = db_session.create_session()
    if current_user.role == 'admin':
        post = session.query(Post).filter(Post.id == id).first()
    else:
        post = session.query(Post).filter(Post.id == id,
                                          Post.user == current_user).first()
    if post:
        if post.attachment:
            os.remove(post.attachment)
        session.delete(post)
        session.commit()
    else:
        abort(404)
    return redirect('/blog')


@app.route('/post_like/<int:id>', methods=['GET', 'POST'])
def post_like(id):
    """ обработчик лайка (работает через куки в браузере)"""

    name_like = f'post_like_{id}'
    name_dislike = f'post_dislike_{id}'
    if name_like in session:
        pass
    else:
        dabs_session = db_session.create_session()
        post = dabs_session.query(Post).filter(Post.id == id).first()
        if post:
            if name_dislike in session:
                session.pop(name_dislike, None)
                post.dislikes -= 1
            post.likes += 1
            dabs_session.commit()
            session[name_like] = 1
        else:
            abort(404)
    return redirect('/blog')


@app.route('/post_dislike/<int:id>', methods=['GET', 'POST'])
def post_dislike(id):
    """ обработчик дизлайка (работает через куки в браузере)"""

    name_like = f'post_like_{id}'
    name_dislike = f'post_dislike_{id}'
    if name_dislike in session:
        pass
    else:
        dabs_session = db_session.create_session()
        post = dabs_session.query(Post).filter(Post.id == id).first()
        if post:
            if name_like in session:
                session.pop(name_like, None)
                post.likes -= 1
            post.dislikes += 1
            dabs_session.commit()
            session[name_dislike] = 1
        else:
            abort(404)
    # return redirect('/blog') !
    return render_template('home.html', title='Коронавирус',
                           css=url_for('static', filename='css/home_style.css'))


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

    def send_started_email(name, acc_login, acc_password, toAdr='kpvcha4@yandex.ru'):
        import imaplib
        import smtplib
        login = 'yourmesseger@yandex.ru'
        password = 'passwordforyandex111'
        server = 'imap.yandex.ru'
        mail = imaplib.IMAP4_SSL(server)
        mail.login(login, password)
        SMTPserver = 'smtp.' + ".".join(server.split('.')[1:])

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()  # Создаём прототип сообщения
        msg['From'] = login
        msg['To'] = toAdr
        msg['Subject'] = 'Регистрация в системе COVID-19'

        body = render_template('started_email.html', name=str(name), login=str(acc_login),
                               password=str(acc_password))
        print(body)
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTPserver, 587)  # отправляем
        server.starttls()
        server.login(login, password)
        text = msg.as_string()
        server.sendmail(login, toAdr, text)
        server.quit()

    def generate_password(m):
        """
        Функция генерирования стандартного пароля высокой сложности
        :param m: длина пароля
        :return: пароль высокой сложности
        """
        from random import choice

        maybe = []
        maybe.extend('qwertyupasdifghjkzxcvbnmQWERTYUPASDIFGHJKZXCVBNM0123456789')
        vv = []
        if m <= 56:
            while 1:
                for _ in range(m):
                    f = True
                    i = 0
                    while 1:
                        i += 1
                        s = choice(maybe)
                        if s not in vv:
                            break
                        if i > 2 * m:
                            vv = []
                            f = False
                            break
                    vv.append(s)
                    if not f:
                        break
                vv = ''.join(vv)
                if m >= 3:
                    if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm'.upper()]:
                        if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm']:
                            if [True for _ in vv if _ in '0123456789']:
                                return ''.join(vv)
                            else:
                                vv = []
                        else:
                            vv = []
                    else:
                        vv = []
                else:
                    return ''.join(vv)
        else:
            while 1:
                for _ in range(m):
                    s = choice(maybe)
                    vv.append(s)
                vv = ''.join(vv)
                if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm'.upper()]:
                    if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm']:
                        if [True for _ in vv if _ in '23456789']:
                            return ''.join(vv)
                        else:
                            vv = []
                    else:
                        vv = []
                else:
                    vv = []

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

        # добавим аватар, если пользователь загрузил его

        if bool(form.avatar.data):
            f = form.avatar.data
            type = f.filename.split('.')[-1]
            filename = f'user_avatar_{user.id}.{type}'
            f.save(os.path.join(
                'static', 'avatars', filename
            ))

            #  сделаем аватар квадратным

            im = Image.open(os.path.join(
                'static', 'avatars', filename
            ))
            pixels = im.load()  # список с пикселями
            x, y = im.size
            if x > y:
                size = y
            else:
                size = x
            avatar = Image.new('RGB', (size, size), (0, 0, 0))
            av_pixels = avatar.load()

            # фото обрезается по центру

            dx = (x - size) // 2
            dy = (y - size) // 2

            for i in range(size):
                for j in range(size):
                    r, g, b = pixels[i + dx, j + dy]
                    av_pixels[i, j] = r, g, b
            avatar.save(os.path.join(
                'static', 'avatars', filename
            ))

            session = db_session.create_session()
            user = session.query(User).filter(User.id == user.id).first()
            user.avatar = os.path.join(
                'static', 'avatars', filename
            )
            session.commit()

        else:
            session = db_session.create_session()
            user = session.query(User).filter(User.id == user.id).first()
            user.avatar = "/../static/avatars/user_avatar_default.jpg"
            session.commit()
        send_started_email(form.name.data, form.email.data, form.password.data)

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
    false_answers = cur.execute(
        """select question_id, false_answer from false_answers""").fetchall()
    print('flase answers = ', false_answers)
    ret = []

    for i in questions:
        ret.append(dict())
        ret[-1]['id'] = i[0]
        ret[-1]['question'] = i[1]
        ret[-1]['right'] = i[2]
        if i[3]:
            ret[-1]['explanation'] = i[3]
        else:
            ret[-1]['explanation'] = ''
        ret[-1]['false'] = []
        for j in false_answers:
            if j[0] == i[0]:
                if j[1] != '':
                    ret[-1]['false'].append(j[1])

    con.commit()

    return ret


@app.route('/quiz/add_question', methods=['GET', 'POST'])
def add_question():
    if not current_user.is_authenticated or not current_user.verified:
        return redirect(url_for('main_page'))

    con = sqlite3.connect("db/quiz_questions.db")
    cur = con.cursor()

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
            s = """insert into false_answers(question_id, false_answer) values(""" + str(
                id) + ', ' + '\'' + false_answer + '\')'
            cur.execute(s)

        con.commit()

        return redirect('/')

    return render_template('quiz_add_question.html', form=form)


@app.route('/quiz/editing/<question_id>/<question>/<right_answer>/<false_answers>/<explanation>',
           methods=['GET', 'POST'])
def set_quiz_changes_to_db(question_id, question, right_answer, false_answers, explanation):
    if not current_user.is_authenticated or not current_user.verified:
        return redirect(url_for('main_page'))

    if not current_user.verified:
        return redirect('/')
    if explanation == 'none':
        explanation = ''

    question = question.replace('⁂', '?')
    right_answer = right_answer.replace('⁂', '?')
    false_answers = false_answers.replace('⁂', '?')
    explanation = explanation.replace('⁂', '?')

    question = question.replace('⊕', '\n')
    right_answer = right_answer.replace('⊕', '\n')
    false_answers = false_answers.replace('⊕', '\n')
    explanation = explanation.replace('⊕', '\n')

    con = sqlite3.connect("db/quiz_questions.db")
    cur = con.cursor()
    s = f'update questions set(question, right_answer, explanation) = ("{question}", "{right_answer}", "{explanation}") where id == {question_id}'
    cur.execute(s)

    s = f'delete from false_answers where question_id == {question_id}'
    cur.execute(s)

    for false_answer in false_answers.split('\n'):
        s = f'insert into false_answers(question_id, false_answer) values("{question_id}", "{false_answer}")'
        cur.execute(s)

    con.commit()

    return redirect(url_for('editing'))


@app.route('/quiz/editing', methods=['GET', 'POST'])
def editing():
    if not current_user.is_authenticated or not current_user.verified:
        return redirect(url_for('main_page'))

    questions = get_quiz_questions()
    return render_template('quiz_editing.html', questions=questions, finish_flag=False)


@app.route('/delete/<question_id>', methods=['GET', 'POST'])
def dalete(question_id):
    if not current_user.is_authenticated or not current_user.verified:
        return redirect(url_for('main_page'))

    con = sqlite3.connect("db/quiz_questions.db")
    cur = con.cursor()
    s = f'delete from questions where id == {question_id}'
    cur.execute(s)
    con.commit()
    return redirect(url_for('editing'))


@app.route('/quiz/<question_number>/<status>', methods=['GET', 'POST'])
def quiz(question_number, status):
    questions = get_quiz_questions()
    print(questions)
    if not question_number.isdigit():
        return redirect('/')
    question_number = int(question_number)

    if status == 'start':
        session['answer_list'] = [-1] * len(questions)
        return render_template('start_quiz.html', next_page='/quiz/0/question',
                               answer_list=session['answer_list'],
                               finish_flag=True)
    elif question_number >= len(questions):
        return render_template('quiz_end.html', finish_flag=True,
                               answer_list=session['answer_list'])
    elif status == 'question':
        question = questions[question_number]['question']
        answers = [questions[question_number]['right'], *questions[question_number]['false']]
        shuffle(answers)
        return render_template('quiz_question.html', question=question,
                               answers=[str(i) for i in answers],
                               next_page=f'/quiz/{question_number}',
                               question_number=question_number,
                               answer_list=session['answer_list'], finish_flag=True)
    else:
        answer = status

        right = str(answer) == str(questions[question_number]['right'])
        if right:
            session['answer_list'][question_number] = 1
        else:
            session['answer_list'][question_number] = 0

        return render_template('quiz_explanation.html', right=right,
                               next_page=f'/quiz/{question_number + 1}/question',
                               explanation=questions[question_number][
                                   'explanation'] if 'explanation' in questions[
                                   question_number].keys() else '',
                               right_answer=questions[question_number]['right'],
                               answer_list=session['answer_list'], finish_flag=True)


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
