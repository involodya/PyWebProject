import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    right_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    explanation = sqlalchemy.Column(sqlalchemy.String)
