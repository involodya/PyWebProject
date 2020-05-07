import _thread as thread
import datetime
import os
from random import shuffle
from dotenv import load_dotenv

from flask import Flask, render_template, url_for, redirect, request, abort, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.false_answers import FalseAnswer
from data.posts import Post
from data.questions import Question
from data.regions import Region
from data.users import User

from forms import MakeQuestionForm, ProfileForm, RegisterForm, LoginForm, PostForm

from functions import add_avatar, get_quiz_questions

#  restful
from flask_restful import reqparse, abort, Api, Resource
from restful import posts_resource, regions_resource

# настройки приложения
app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
quiz_results = dict()


@app.route('/')
def main_page():
    """ обработчик главной страницы """

    return render_template('home.html', title='Коронавирус',
                           css=url_for('static', filename='css/home_style.css'))


@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    """ обработчик страницы профиля """

    form = ProfileForm()
    session = db_session.create_session()
    profile = session.query(User).filter(User.id == current_user.id).first()

    if request.method == "GET":
        form.email.data = profile.email
        form.surname.data = profile.surname
        form.name.data = profile.name
        form.age.data = profile.age
        form.about.data = profile.about
        form.education.data = profile.education
        form.speciality.data = profile.speciality

    if form.validate_on_submit():
        profile.surname = form.surname.data
        profile.name = form.name.data
        profile.age = form.age.data
        profile.about = form.about.data
        profile.education = form.education.data
        profile.speciality = form.speciality.data
        session.commit()

        if bool(form.avatar.data):
            add_avatar(form.avatar.data, current_user)

    return render_template('profile.html', title='Профиль', form=form,
                           css=url_for('static', filename='css/profile_style.css'))


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

        post_id = session.query(Post).order_by(Post.id.desc()).first().id

        # Параллельным процессом запускаем рассыку новости всем зарегистрированным пользователям
        thread.start_new_thread(os.system, (f'python send_news_emails.pyw --id {post_id}',))

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
    global post
    dabs_session = db_session.create_session()
    post = dabs_session.query(Post).filter(Post.id == id).first()

    name_like = f'post_like_{id}'
    name_dislike = f'post_dislike_{id}'

    if name_like in session.keys() and session[name_like]:
        post.likes -= 1
        session[name_like] = None
    else:
        post.likes += 1
        session[name_like] = 1
        if name_dislike in session and session[name_dislike]:
            session[name_dislike] = None
            post.dislikes -= 1

    dabs_session.commit()

    return f'{post.likes} {post.dislikes} {id}'


@app.route('/post_dislike/<int:id>', methods=['GET', 'POST'])
def post_dislike(id):
    """ обработчик дизлайка (работает через куки в браузере)"""
    global post
    dabs_session = db_session.create_session()
    post = dabs_session.query(Post).filter(Post.id == id).first()

    name_like = f'post_like_{id}'
    name_dislike = f'post_dislike_{id}'

    if name_dislike in session.keys() and session[name_dislike]:
        post.dislikes -= 1
        session[name_dislike] = None
    else:
        post.dislikes += 1
        session[name_dislike] = 1
        if name_like in session and session[name_like]:
            session[name_like] = None
            post.likes -= 1

    dabs_session.commit()

    return f'{post.likes} {post.dislikes} {id}'


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
    if current_user.is_authenticated:
        return redirect('/profile')

    def send_started_email(name, acc_login, acc_password, to_adr):
        """ Функция отправки сообщения об успешной регистрации """
        import imaplib
        import smtplib
        server = 'imap.yandex.ru'
        mail = imaplib.IMAP4_SSL(server)
        mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        SMTPserver = 'smtp.' + ".".join(server.split('.')[1:])

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart()  # Создаём прототип сообщения
        msg['From'] = EMAIL_LOGIN
        msg['To'] = to_adr
        msg['Subject'] = 'Регистрация в системе COVID-19'

        body = render_template('started_email.html', name=str(name), login=str(acc_login),
                               password=str(acc_password))
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTPserver, 587)  # отправляем
        server.starttls()
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_LOGIN, to_adr, text)
        server.quit()

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

        add_avatar(form.avatar.data, user)

        send_started_email(form.name.data, form.email.data, form.password.data, form.email.data)

        return redirect('/login')
    return render_template('join.html', title='Регистрация', form=form,
                           css=url_for('static', filename='css/join_style.css'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ обратчик страницы с авторизацией """
    if current_user.is_authenticated:
        return redirect('/profile')

    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form,
                               css=url_for('static', filename='css/login_style.css'))
    return render_template('login.html', title='Авторизация', form=form,
                           css=url_for('static', filename='css/login_style.css'))


@app.route('/quiz/add_question', methods=['GET', 'POST'])
def add_question():
    """" добавление вопросов """

    # Только админ может добавлять вопросы
    if not current_user.is_authenticated or not current_user.verified or not current_user.role == 'admin':
        return redirect(url_for('main_page'))

    session = db_session.create_session()
    question = Question()

    form = MakeQuestionForm()
    if form.validate_on_submit():  # Если форма заполнена, записываем информацию о вопроме в базу данных
        question.question = form.question.data
        question.right_answer = form.right_answer.data
        question.explanation = form.explanation.data

        session.add(question)  # Запись вопроса в базу данных

        session.commit()

        id = question.id

        for i in form.false_answers.data.split(
                '\n'):  # Неправильные вопросы в форме разделены переводами строк
            false_answer = FalseAnswer()
            false_answer.false_answer = i
            false_answer.question_id = id
            false_answer.question = question
            session.add(false_answer)  # записываем неправильный вопрос в базу данных

        session.commit()

        return redirect(url_for('editing'))

    return render_template('quiz_add_question.html', title='Викторина', form=form)


@app.route('/quiz/editing/<question_id>/<question_s>/<right_answer>/<false_answers>/<explanation>',
           methods=['GET', 'POST'])
def set_quiz_changes_to_db(question_id, question_s, right_answer, false_answers, explanation):
    """ Функция изменения вопроса """

    # Изменять вопросы може только админ
    if not current_user.is_authenticated or not current_user.verified or not current_user.role == 'admin':
        return redirect(url_for('main_page'))

    # При передаче данных пустое explanation (объяснение) передается как none, но хранить и выводить пользователю нужно
    # пустую строку
    if explanation == 'none':
        explanation = ''

    session = db_session.create_session()

    # Вопросительный знак и перевод строки некоректно передаются через адресную строку, пожтому перед передачей
    # они заменяются на редко используемые символы, а при приеме заменяются обратно
    question_s = question_s.replace('⁂', '?')
    right_answer = right_answer.replace('⁂', '?')
    false_answers = false_answers.replace('⁂', '?')
    explanation = explanation.replace('⁂', '?')

    question_s = question_s.replace('⊕', '\n')
    right_answer = right_answer.replace('⊕', '\n')
    false_answers = false_answers.replace('⊕', '\n')
    explanation = explanation.replace('⊕', '\n')

    # изменение данных вопроса
    question = session.query(Question).filter(Question.id == question_id).first()

    question.question = question_s
    question.right_answer = right_answer
    question.explanation = explanation

    false_answers_db = session.query(FalseAnswer)
    for false_answer in false_answers_db:
        if false_answer.question_id == question_id:
            session.delete(false_answer)

    for false_answer_s in false_answers.split('\n'):
        false_answer = FalseAnswer()
        false_answer.false_answer = false_answer_s
        false_answer.question_id = question_id
        session.add(false_answer)

    session.commit()

    return redirect(url_for('editing'))


@app.route('/quiz/editing', methods=['GET', 'POST'])
def editing():
    """ страница редактирования вопроса """

    # редактировать вопрос может только админ
    if not current_user.is_authenticated or not current_user.verified or not current_user.role == 'admin':
        return redirect(url_for('main_page'))

    # получение вопросов и передача их в шаблонизатор
    questions = get_quiz_questions()
    return render_template('quiz_editing.html', title='Викторина', questions=questions,
                           finish_flag=False)


@app.route('/delete/<question_id>', methods=['GET', 'POST'])
def delete_handler(question_id):
    """ Удаление вопроса """

    # Удалять вопрос может только админ
    if not current_user.is_authenticated or not current_user.verified or not current_user.role == 'admin':
        return redirect(url_for('main_page'))

    session = db_session.create_session()
    session.query(Question).filter(Question.id == question_id).delete()
    session.commit()

    return redirect(url_for('editing'))


@app.route('/quiz/<question_number>/<status>', methods=['GET', 'POST'])
def quiz(question_number, status):
    """ страница прохождения викторины """

    # Викторину могут проходить все, в том числе и не авторизованные пользователи.
    # Единственная разница в том, что у авторизованных пользователей результат прохождения сохраняется на сервере
    # и они в любой момент могут его посмотреть, а у неавторизовыных пользователей результат сохраняется
    # в session['answer_list'] и хранится временно

    global quiz_results, questions_id

    if status != 'start':
        # Если пользователь не имеет необходимых массивов для хранения результата,
        # его перенаправляет в начало викторины, где эти массивы и создаются
        if 'questions' not in session.keys():
            return redirect('/quiz/0/start')
        if not session['questions']:
            return redirect('/quiz/0/start')

    # Если неправильно введен номер вопроса, пользователя перенаправляют в начало викторины
    if not question_number.isdigit():
        return redirect('/quiz/0/start')
    question_number = int(question_number)

    if status == 'start':
        # Начало викторины, создание массивов для хранения результата
        session['questions'] = get_quiz_questions()
        questions_id = [i['id'] for i in session['questions']]
        session['answer_list'] = [-1] * len(session['questions'])

        if current_user.is_authenticated:
            if current_user.email not in quiz_results.keys():
                quiz_results[current_user.email] = dict()
            for i in questions_id:
                quiz_results[current_user.email][i] = -1

        return render_template('start_quiz.html', title='Викторина', next_page='/quiz/0/question',
                               answer_list=[quiz_results[current_user.email][i] for i in
                                            questions_id] if current_user.is_authenticated else
                               session[
                                   'answer_list'],
                               finish_flag=True)
    elif question_number >= len(session['questions']):
        # Конец викторины
        return render_template('quiz_end.html', title='Викторина', finish_flag=True,
                               answer_list=[quiz_results[current_user.email][i] for i in
                                            questions_id] if current_user.is_authenticated else
                               session['answer_list'])
    elif status == 'question':
        # Отображение вопросы перед пользователем
        question = session['questions'][question_number]['question']
        answers = [session['questions'][question_number]['right'],
                   *session['questions'][question_number]['false']]

        # Рандомное ответов, чтобы они не оказывались каждый раз в одном и том-же порядке
        shuffle(answers)

        return render_template('quiz_question.html', title='Викторина', question=question,
                               answers=[str(i) for i in answers],
                               next_page=f'/quiz/{question_number}',
                               question_number=question_number,
                               answer_list=[quiz_results[current_user.email][i] for i in
                                            questions_id] if current_user.is_authenticated else
                               session['answer_list'], finish_flag=True)
    else:
        # Пользователь дал ответ и его нужно проверить
        answer = status

        right = str(answer) == str(session['questions'][question_number]['right'])
        if current_user.is_authenticated:
            if right:
                quiz_results[current_user.email][session['questions'][question_number]['id']] = 1
            else:
                quiz_results[current_user.email][session['questions'][question_number]['id']] = 0
        else:
            if right:
                session['answer_list'][question_number] = 1
            else:
                session['answer_list'][question_number] = 0

        return render_template('quiz_explanation.html', title='Викторина', right=right,
                               next_page=f'/quiz/{question_number + 1}/question',
                               explanation=session['questions'][question_number][
                                   'explanation'] if 'explanation' in session['questions'][
                                   question_number].keys() else '',
                               right_answer=session['questions'][question_number]['right'],
                               answer_list=[quiz_results[current_user.email][i] for i in
                                            questions_id] if current_user.is_authenticated else
                               session['answer_list'], finish_flag=True)


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
    db_session.global_init("db/database.sqlite")

    # Загружаем переменные среды из файла
    load_dotenv()
    # Теперь будто бы переданы переменные
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    EMAIL_LOGIN = os.environ.get('EMAIL_LOGIN')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

    # restful-api
    # список постов
    api.add_resource(posts_resource.PostListResource, '/api/posts')
    # один пост
    api.add_resource(posts_resource.PostResource, '/api/posts/<int:post_id>')
    # список регионов
    api.add_resource(regions_resource.RegionListResource, '/api/regions')
    # один регион
    api.add_resource(regions_resource.RegionResource, '/api/regions/<int:region_id>')

    # запуск приложения
    # глобальный запуск
    # run_with_ngrok(app)
    # app.run()
    # локальный запуск
    app.run(port=8080, host='127.0.0.1')
