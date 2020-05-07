import os

from PIL import Image

from data import db_session
from data.false_answers import FalseAnswer
from data.questions import Question
from data.users import User
import cv2


def get_quiz_questions():
    """ получение вопросов для викторины """

    session = db_session.create_session()
    questions = session.query(Question)
    false_answers = session.query(FalseAnswer)

    # ret список словарей, каждый из словарей описывает один изз вопросов
    # словарь получается из двух массивов, вопросов и неправильных ответов,
    # которые в свою очередь сохранены в базе данных

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
    PADDING = 10

    # добавим аватар, если пользователь загрузил его

    if bool(f):
        type = f.filename.split('.')[-1]
        filename = f'user_avatar_{user.id}.{type}'
        print(f'user id = {user.id}')
        f.save(os.path.join(
            'static', 'avatars', filename
        ))

        #  сделаем аватар квадратным

        image_path = os.path.join('static', 'avatars', filename)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(10, 10)
        )
        faces_detected = "Лиц обнаружено: " + format(len(faces))
        print(faces_detected)

        height, width, channels = image.shape
        right_down = [0, height]
        left_up = [width, 0]

        for x, y, w, h in faces:
            left_up[0] = min(left_up[0], x - PADDING)
            left_up[1] = max(left_up[1], y + w + PADDING)

            right_down[0] = max(right_down[0], x + h + PADDING)
            right_down[1] = min(right_down[1], y - PADDING)

        szx, szy = right_down[0] - left_up[0], right_down[1] - left_up[1]
        d = abs(szx - szy)
        if szx > szy:
            left_up[1] -= d // 2
            right_down[1] += d // 2
        elif szx < szy:
            left_up[0] -= d // d
            right_down[0] += d // 2

        im = Image.open(image_path)

        cutted_im = im.crop((*left_up, *right_down))
        cutted_im.save(os.path.join('static', 'avatars', filename))

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
