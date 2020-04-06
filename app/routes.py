from app import app
from flask import render_template, flash, redirect, url_for, request, session
from app.data.db_session import create_session
from app.data.user import User

@app.route('/')
def index():
    db = create_session()
    users = ', '.join([str(i) for i in db.query(User)])
    return 'All users  ' + users
