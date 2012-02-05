var currentQuestion = null;
var currentQuestionSource = null;
var currentQuestionNewResult = {};

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

    var category_id = currentQuestion.category;
    var category_name = game.categories[category_id].name;
    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html(currentQuestion.value);
    $('#question_area #question').html(currentQuestion.question);
    $('#question_area #answer').html(currentQuestion.answer);
    $('#question_area').show('slow');
};

displayAlreadyAskedQuestion = function() {
    hideCurrentQuestion();

    var category_id = currentQuestion.category;
    var category_name = game.categories[category_id].name;
    $('#already_asked_area #header_category').html(category_name);
    $('#already_asked_area #header_value').html(currentQuestion.value);
    $('#already_asked_area ul').html('');

    var summary = getCurrentQuestionLastResultSummary();
    for (var i in summary) {
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

redoAlreadyAskedQuestion = function() {
    undoCurrentQuestionLastResult();
    displayCurrentQuestion();
};

nobodyGotIt = function() {
    finishCurrentQuestion();
};

finishCurrentQuestion = function() {
    processCurrentQuestionResults();
    currentQuestion.result = currentQuestionNewResult;
    markCurrentQuestionAsAsked();
    hideCurrentQuestion();

    $.post('/update_game/' + game.pk + '/', 
            currentQuestion,
            function(data) {
                $('#ajax_status').html('success').fadeIn().delay(800).fadeOut();
            },
            'json');

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
    for (var player_pk in currentQuestionNewResult) {
        adjustScore(player_pk, currentQuestionNewResult[player_pk]);
    }
};

undoCurrentQuestionLastResult = function() {
    for (var player_pk in currentQuestion.result) {
        adjustScore(player_pk, -currentQuestion.result[player_pk]);
    }
};

getCurrentQuestionLastResultSummary = function() {
    var results = [];
    var someoneGotIt = false;

    for (var player_pk in currentQuestion.result) {
        var name = '<strong>' + game.players[player_pk].username + '</strong>';
        var score_change = currentQuestion.result[player_pk];
        if (score_change > 0) {
            someoneGotIt = true;
        }

        var str = name + ' got the question ';
        str += ((score_change > 0) ? '<span class="right">right</span>' : '<span class="wrong">wrong</span>') + ' and ';
        str += ((score_change > 0) ? 'won' : 'lost') + ' ';
        str += ((score_change > 0) ? score_change : -score_change) + ' points.';

        results.push(str);
    }

    if (!someoneGotIt) {
        results.push('No one answered correctly.');
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
    $('#score_board #score' + player_pk).fadeOut().html(score).fadeIn();
};

$(document).ready(function(){
    $('#question_area').hide();
    $('#already_asked_area').hide();
    $('#ajax_status').hide();
});
