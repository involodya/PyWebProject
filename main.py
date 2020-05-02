from flask import Flask, render_template, url_for, redirect, request, abort, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.regions import Region
from data.posts import Post
from forms import RegisterForm, LoginForm, PostForm
import datetime
import os
from PIL import Image

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

    return render_template('home.html', title='Коронавирус', css=url_for('static', filename='css/home_style.css'))


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
