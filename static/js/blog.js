function funkSuccess(data){
    data = data.split(' ');
    likes = data[0];
    dislikes = data[1];
    id = data[2];
    td_list = $('#' + id).find('table').children();
    a_list = $(td_list[td_list.length - 1]).find('a');
    $(a_list[0]).html('👍 ' + likes);
    $(a_list[1]).html('👎 ' + dislikes);
}

$(document).ready(function(){
    $('.mark').click(function(){
        class_list = $(this).attr('class').split(' ');
        id = class_list[0];
        for (let clas of class_list) {
            if (clas == 'like') {
                $.ajax({
                    url: '/post_like/' + id,
                    success: funkSuccess
                });

            }
            else if (clas == 'dislike'){
                $.ajax({url: '/post_dislike/' + id, success: funkSuccess});
            }
        }

    });
});