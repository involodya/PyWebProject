def generate_password(m):
    """
    Функция генерирования стандартного пароля высокой сложности
    :param m: длина пароля
    :return: пароль высокой сложности
    """
    from random import choice

    maybe = []
    maybe.extend('qwertyupasdifghjkzxcvbnmQWERTYUPASDIFGHJKZXCVBNM0123456789')
    vv = []
    if m <= 56:
        while 1:
            for _ in range(m):
                f = True
                i = 0
                while 1:
                    i += 1
                    s = choice(maybe)
                    if s not in vv:
                        break
                    if i > 2 * m:
                        vv = []
                        f = False
                        break
                vv.append(s)
                if not f:
                    break
            vv = ''.join(vv)
            if m >= 3:
                if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm'.upper()]:
                    if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm']:
                        if [True for _ in vv if _ in '0123456789']:
                            return ''.join(vv)
                        else:
                            vv = []
                    else:
                        vv = []
                else:
                    vv = []
            else:
                return ''.join(vv)
    else:
        while 1:
            for _ in range(m):
                s = choice(maybe)
                vv.append(s)
            vv = ''.join(vv)
            if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm'.upper()]:
                if [True for _ in vv if _ in 'qwertyulpasdfghjkzxcvbnm']:
                    if [True for _ in vv if _ in '23456789']:
                        return ''.join(vv)
                    else:
                        vv = []
                else:
                    vv = []
            else:
                vv = []
