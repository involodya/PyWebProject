import sqlalchemy


from .db_session import SqlAlchemyBase


class Region(SqlAlchemyBase):
    __tablename__ = 'regions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cases = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    cured = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    deaths = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    lon = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    lat = sqlalchemy.Column(sqlalchemy.Float, nullable=True)