html = document.querySelector('html');
a = [['--background-color', '#002137'],
    ['--nav-background-color', '#000305'],
    ['--text-color', '#999999'],

    ['--quiz-a-text-color', '#999999'],
    ['--quiz-a-text-hover-color', '#888888'],
    ['--quiz-a-color', '#ffa500'],
    ['--quiz-a-hover-color', '#ffba42'],
    ['--nav-color', '#242424'],
    ['--blog-content-unit-color', '#222222'],
    ['--second-background-color', '#888888'],
    ['--second-text-color', 'white'],
    ['--input-border-color', '#999999']];
for (let i of a) {
    html.style.setProperty(i[0], i[1]);
}