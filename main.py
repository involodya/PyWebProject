from flask import Flask, render_template, url_for
from pars_html import pars_html

app = Flask(__name__)


@app.route('/yandex')
def return_yandex_page():
    return render_template('base.html', css=url_for('static', filename='css/style.css'))


@app.route('/1')
def return_yandex1_page():
    return render_template('yandex1.html', css=url_for('static', filename='css/style.css'))


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
