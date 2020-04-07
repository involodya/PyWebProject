from flask import Flask, render_template
from app import app
from app.data.db_session import create_session


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8980', debug=True)
