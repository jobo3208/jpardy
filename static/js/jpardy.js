currentQuestion = null;

test = null;

$(document).ready(function(){
    $('#question_area').hide();

    player_table = $('<table/>').appendTo($('#question_area #who'));

    for (player in game.players) {
        row = $('<tr/>').appendTo(player_table);

        $('<td/>').appendTo(row)
            .text(game.players[player].username);

        correct_td = $('<td/>').appendTo(row);
        $('<button/>').appendTo(correct_td)
            .addClass('correct_button')
            .data('player', player);
        
        incorrect_td = $('<td/>').appendTo(row);
        $('<button/>').appendTo(incorrect_td)
            .addClass('incorrect_button')
            .data('player', player);
    }

    $('#question_area #who button').click(function () {
        $(this).attr('disabled', 'disabled');
        $(this).removeClass().addClass('disabled_button');
    });
});

displayQuestion = function(question) {
    currentQuestion = question;
    category_id = question.category;
    category_name = game.categories[category_id].name;
    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html(question.value);
    $('#question_area #question').html(question.question);
    $('#question_area #answer').html(question.answer);
    $('#question_area').show('slow');
};

hideQuestion = function() {
    currentQuestion = null;
    $('#question_area').hide('slow');
};

correct = function(player_pk, question) {
    adjustScore(player_pk, question.value);
};

incorrect = function(player_pk, question) {
    adjustScore(player_pk, -question.value);
};

nobodyGotIt = function(question) {
    alert('nobody got it!');
};

adjustScore = function(player_pk, diff) {
    game.players[player_pk].score += diff;
    displayScore(player_pk, game.players[player_pk].score);
};

displayScore = function(player_pk, score) {
    $('#score_board #score' + player_pk).html(score);
};
