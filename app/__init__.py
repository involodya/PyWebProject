from flask import Flask
from app.data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
db_session.global_init('database.db')

from app import routes
