# Пример работы с базой данных


from app.data.db_session import global_init, create_session
from app.data.user import User

global_init('database.db')
db = create_session()
    
user = User()
user.name = "admin"
user.hashed_password = '123'

db.add(user)

db.commit()

for user in db.query(User):
    print(user)


