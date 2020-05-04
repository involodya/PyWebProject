$(document).ready(function(){
    $('.open-edit').on('click', function(){
        image = $(this).children('img');
        edit_question = $(this).parent().children('.edit-question');
        if (image.attr('src') == 'https://img.icons8.com/ios-glyphs/15/000000/sort-down.png'){
            image.attr('src', 'https://img.icons8.com/ios-glyphs/15/000000/sort-right.png')
            edit_question.css('display', 'none')

        }else {
            image.attr('src', 'https://img.icons8.com/ios-glyphs/15/000000/sort-down.png');
            edit_question.css('display', 'block');
        }
    });
    $('.commit-question-changes').on('mouseover', function(){
        class_ist = $(this).attr('class').split(' ');
        s = '/quiz/editing/' + class_ist[class_ist.length - 1];
        textarea_list = $(this).parent().find('textarea');
        for (let i = 0; i < textarea_list.length; i++){
            val = $(textarea_list[i]).val();
            if (val == '') s += '/none';
            else{
                s += '/';
                for (let c of val){
                    if (c == '?')
                        s += '⁂';
                    else if (c == '\n')
                        s += '⊕';
                    else
                        s += c;
                }
            }
        }
        $(this).attr('href', s);
    });
});