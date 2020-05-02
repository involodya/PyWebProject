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
    app.run(port=8080, host='127.0.0.1')


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
        session.delete(post)
        session.commit()
    else:
        abort(404)
    return redirect('/blog')


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
