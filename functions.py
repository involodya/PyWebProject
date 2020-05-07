from data import db_session
from data.questions import Question
from data.false_answers import FalseAnswer


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


if __name__ == '__main__':
    print(get_quiz_questions())

