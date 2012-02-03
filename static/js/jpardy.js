currentQuestion = null;
currentQuestionSource = null;
currentQuestionNewResult = {};

selectQuestion = function(source, question_pk) {
    currentQuestion = game.questions[question_pk];
    currentQuestionSource = source;

    if (currentQuestion.asked) {
        displayAlreadyAskedQuestion();
    }
    else {
        displayCurrentQuestion();
    }
};

displayCurrentQuestion = function() {
    resetAnswerArea();
    hideAlreadyAskedQuestion();

    category_id = currentQuestion.category;
    category_name = game.categories[category_id].name;
    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html(currentQuestion.value);
    $('#question_area #question').html(currentQuestion.question);
    $('#question_area #answer').html(currentQuestion.answer);
    $('#question_area').show('slow');
};

displayAlreadyAskedQuestion = function() {
    category_id = currentQuestion.category;
    category_name = game.categories[category_id].name;
    $('#already_asked_area #header_category').html(category_name);
    $('#already_asked_area #header_value').html(currentQuestion.value);
    $('#already_asked_area ul').html('');

    var summary = getCurrentQuestionLastResultSummary();
    for (i in summary) {
        $('#already_asked_area ul').append('<li>' + summary[i] + '</li>');
    }

    $('#already_asked_area').show('slow');
};

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

hideCurrentQuestion = function() {
    $('#question_area').hide('slow');
};

hideAlreadyAskedQuestion = function() {
    $('#already_asked_area').hide('slow');
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

    addResultToCurrentQuestion(player_pk, currentQuestion.value);
    finishCurrentQuestion();
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

    addResultToCurrentQuestion(player_pk, -currentQuestion.value);
};

cancelCurrentQuestion = function() {
    hideCurrentQuestion();
    resetCurrentQuestion();
};

cancelAlreadyAskedQuestion = function() {
    hideAlreadyAskedQuestion();
    resetCurrentQuestion();
};

nobodyGotIt = function() {
    finishCurrentQuestion();
};

finishCurrentQuestion = function() {
    processCurrentQuestionResults();
    currentQuestion.result = currentQuestionNewResult;
    markCurrentQuestionAsAsked();
    hideCurrentQuestion();
    resetCurrentQuestion();
};

addResultToCurrentQuestion = function(player_pk, score_change) {
    currentQuestionNewResult[player_pk] = score_change;
};

markCurrentQuestionAsAsked = function() {
    currentQuestion.asked = true;
    $(currentQuestionSource).removeClass().addClass('asked_question');
};

processCurrentQuestionResults = function() {
    for (player_pk in currentQuestionNewResult) {
        adjustScore(player_pk, currentQuestionNewResult[player_pk]);
    }
};

undoCurrentQuestionLastResult = function() {
    for (player_pk in currentQuestion.result) {
        adjustScore(player_pk, -currentQuestion.result[player_pk]);
    }
};

getCurrentQuestionLastResultSummary = function() {
    var results = [];
    for (player_pk in currentQuestion.result) {
        var name = game.players[player_pk].username;
        var score_change = currentQuestion.result[player_pk];
        var str = name + ' got the question ';
        str += ((score_change > 0) ? 'right' : 'wrong') + ' and ';
        str += ((score_change > 0) ? 'won' : 'lost') + ' ';
        str += ((score_change > 0) ? score_change : -score_change) + ' points.';

        results.push(str);
    }

    return results;
};

resetCurrentQuestion = function() {
    currentQuestion = null;
    currentQuestionSource = null;
    currentQuestionNewResult = {};
};

adjustScore = function(player_pk, diff) {
    game.players[player_pk].score += diff;
    displayScore(player_pk, game.players[player_pk].score);
};

displayScore = function(player_pk, score) {
    $('#score_board #score' + player_pk).html(score).fadeOut().fadeIn();
};

$(document).ready(function(){
    $('#question_area').hide();
    $('#already_asked_area').hide();
});
