html = document.querySelector('html');
a = [['--background-color', '#999999'],
    ['--text-color', '#222222'],

    ['--quiz-a-text-color', '#999999'],
    ['--quiz-a-text-hover-color', '#888888'],
    ['--quiz-a-color', '#535efd'],
    ['--quiz-a-hover-color', '#7B68EE'],
    ['--nav-color', '#72848f'],
    ['--content-unit-color', '#999999'],
    ['--second-background-color', 'white'],
    ['--second-text-color', '#222222'],
    ['--input-border-color', '#888888']];
for (let i of a) {
    html.style.setProperty(i[0], i[1]);
}