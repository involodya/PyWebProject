from flask import Flask, render_template, url_for
from data import db_session

app = Flask(__name__)


def main():
    db_session.global_init("db/database.sqlite")
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
def main_page():
    return render_template('base.html', title='матвей')


@app.route('/test')
def test():
    return render_template('test.html', title='матвей')


if __name__ == '__main__':
    main()
