import argparse
import imaplib
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import render_template, Flask

from data import db_session
from data.posts import Post
from data.users import User


def send_news_email(html, toAdr):
    # Загружаем переменные среды из файла
    load_dotenv()
    # Теперь будто бы переданы переменные
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    EMAIL_LOGIN = os.environ.get('EMAIL_LOGIN')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    server = 'imap.yandex.ru'
    mail = imaplib.IMAP4_SSL(server)
    mail.login(EMAIL_LOGIN, EMAIL_PASSWORD)
    SMTPserver = 'smtp.' + ".".join(server.split('.')[1:])

    msg = MIMEMultipart()  # Создаём прототип сообщения
    msg['From'] = EMAIL_LOGIN
    msg['To'] = toAdr
    msg['Subject'] = 'Новость на портале COVID-19'

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP(SMTPserver, 587)  # отправляем
    server.starttls()
    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
    text = msg.as_string()
    server.sendmail(EMAIL_LOGIN, toAdr, text)
    server.quit()


parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int)
post_id = parser.parse_args().id

db_session.global_init("db/database.sqlite")
session = db_session.create_session()
post = session.query(Post).filter(Post.id == post_id).first()

app = Flask(__name__)
with app.app_context():
    html = render_template('news_email.html', post=post)

users = session.query(User).all()

for user in users:
    try:
        send_news_email(html, user.email)
    except Exception as ex:
        print(ex)
