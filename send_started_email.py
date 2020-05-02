def send_started_email(acc_login, acc_password, toAdr='kpvcha4@yandex.ru'):
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
    msg['Subject'] = 'Регистрация в Messenger'

    body = render_template('send_started_email.html', login=str(acc_login),
                           password=str(acc_password))
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(SMTPserver, 587)  # отправляем
    server.starttls()
    server.login(login, password)
    text = msg.as_string()
    server.sendmail(login, toAdr, text)
    server.quit()
