def pars_html():
    import requests
    from bs4 import BeautifulSoup as BS

    r = requests.get('https://yandex.ru/covid19')
    html = BS(r.content, 'html.parser')
    for el in html.select('.special-event__content'):
        with open('static/pars_html.html', 'a', encoding='utf-8') as file:
            file.write(str(el))
