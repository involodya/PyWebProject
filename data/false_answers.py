import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class FalseAnswer(SqlAlchemyBase):
    __tablename__ = 'false_answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    false_answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    question_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("questions.id"))
    question = orm.relation('Question')
