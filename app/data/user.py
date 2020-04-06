import datetime
from sqlalchemy import orm, Column, Integer, String, DateTime
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.name}'