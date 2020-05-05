$(document).ready(function(){
    $('#checkout-button').click(function(){
        circle = $('#circle');
        if (circle.attr('class') == 'circle-left'){
            circle.attr('class', 'circle-right');
            circle.attr('src', 'https://img.icons8.com/ios-filled/20/000000/crescent-moon.png')
        }
        else{
            circle.attr('class','circle-left');
            circle.attr('src', 'https://img.icons8.com/android/20/000000/sun.png');
        }
    });
});