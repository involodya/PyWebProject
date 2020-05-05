import argparse

from data.posts import Post
from data.users import User
from flask import render_template, Flask, url_for

from data import db_session


def send_news_email(html, toAdr):
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
    msg['Subject'] = 'Новость на портале COVID-19'

    msg.attach(MIMEText(html, 'html'))

    server = smtplib.SMTP(SMTPserver, 587)  # отправляем
    server.starttls()
    server.login(login, password)
    text = msg.as_string()
    server.sendmail(login, toAdr, text)
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
