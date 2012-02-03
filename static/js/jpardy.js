currentQuestion = null;

// The button that activated this question.
currentQuestionSource = null;

$(document).ready(function(){
    $('#question_area').hide();
});

displayQuestion = function(source, question) {
    currentQuestion = question;
    currentQuestionSource = source;
    resetAnswerArea();
    category_id = question.category;
    category_name = game.categories[category_id].name;
    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html(question.value);
    $('#question_area #question').html(question.question);
    $('#question_area #answer').html(question.answer);
    $('#question_area').show('slow');
};

// Re-enables buttons and clears result text.
resetAnswerArea = function() {
    $('#answer_area')
        .find('button:even')
            .removeAttr('disabled')
            .removeClass()
            .addClass('correct_button')
        .end()
        .find('button:odd')
            .removeAttr('disabled')
            .removeClass()
            .addClass('incorrect_button')
        .end()
        .find('tr')
            .find('td:last')
                .text('');
};

hideQuestion = function() {
    currentQuestion = null;
    currentQuestionSource = null;
    $('#question_area').hide('slow');
};

correct = function(source, player_pk) {
    // Disable further button pushing and mark answer as correct.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('correct');

    $(currentQuestionSource).removeClass().addClass('asked_question');
    hideQuestion();
};

incorrect = function(source, player_pk) {
    // Disable further button pushing and mark answer as incorrect.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('wrong');
};

nobodyGotIt = function() {
    $(currentQuestionSource).removeClass().addClass('asked_question');
    hideQuestion();
};

adjustScore = function(player_pk, diff) {
    game.players[player_pk].score += diff;
    displayScore(player_pk, game.players[player_pk].score);
};

displayScore = function(player_pk, score) {
    $('#score_board #score' + player_pk).html(score);
};
