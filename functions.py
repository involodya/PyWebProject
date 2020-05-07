import os

from PIL import Image

from data import db_session
from data.false_answers import FalseAnswer
from data.questions import Question
from data.users import User


def get_quiz_questions():
    """ получение вопросов для викторины """

    session = db_session.create_session()
    questions = session.query(Question)
    false_answers = session.query(FalseAnswer)

    ret = []

    for question in questions:
        ret.append(dict())
        ret[-1]['id'] = question.id
        ret[-1]['question'] = question.question
        ret[-1]['right'] = question.right_answer
        if question.explanation:
            ret[-1]['explanation'] = question.explanation
        else:
            ret[-1]['explanation'] = ''
        ret[-1]['false'] = []
        for false_answer in false_answers:
            if false_answer.question_id == question.id:
                if false_answer.false_answer != '':
                    ret[-1]['false'].append(false_answer.false_answer)

    return ret


def add_avatar(f, user):
    # добавим аватар, если пользователь загрузил его

    if bool(f):
        type = f.filename.split('.')[-1]
        filename = f'user_avatar_{user.id}.{type}'
        f.save(os.path.join(
            'static', 'avatars', filename
        ))

        #  сделаем аватар квадратным

        im = Image.open(os.path.join(
            'static', 'avatars', filename
        ))
        pixels = im.load()  # список с пикселями
        x, y = im.size
        if x > y:
            size = y
        else:
            size = x
        avatar = Image.new('RGB', (size, size), (0, 0, 0))
        av_pixels = avatar.load()

        # фото обрезается по центру

        dx = (x - size) // 2
        dy = (y - size) // 2

        for i in range(size):
            for j in range(size):
                r, g, b = pixels[i + dx, j + dy]
                av_pixels[i, j] = r, g, b
        avatar.save(os.path.join(
            'static', 'avatars', filename
        ))

        session = db_session.create_session()
        user = session.query(User).filter(User.id == user.id).first()
        user.avatar = os.path.join(
            'static', 'avatars', filename
        )
        session.commit()

    else:
        session = db_session.create_session()
        user = session.query(User).filter(User.id == user.id).first()
        user.avatar = "/../static/avatars/user_avatar_default.jpg"
        session.commit()


if __name__ == '__main__':
    print(get_quiz_questions())
