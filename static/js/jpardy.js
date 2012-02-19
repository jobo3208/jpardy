var currentQuestion = null;
var currentQuestionSource = null;
var currentQuestionNewResult = {};

var currentDailyDoublePlayer = -1;
var currentDailyDoubleWager = -1;

var finalJpardyPlayers = [];
var finalJpardyWagers = {};

var selectQuestion = function(source, question_pk) {
    currentQuestion = game.questions[question_pk];
    currentQuestionSource = source;
    displayCurrentQuestion();
};


var displayCurrentQuestion = function() {
    hideAll();
    resetAnswerRows();

    if (currentQuestion.asked) {
        displayAlreadyAskedQuestion();
    }
    else if (currentQuestion.daily_double) {
        displayDailyDouble();
    }
    else {
        displayRegularQuestion();
    }
};


var hideAll = function(speed) {
    $('#question_area').hide(speed);
    $('#already_asked_area').hide(speed);
    $('#dd_area').hide(speed);
    $('#proceed_to_final_area').hide(speed);
    $('#final_wager_area').hide(speed);
};


var resetAnswerRows = function() {
    $('#answer_area tr').show();
    $('#question_area #nobody').show();
};


var displayAlreadyAskedQuestion = function() {
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


var getCurrentQuestionLastResultSummary = function() {
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


var displayDailyDouble = function() {
    resetDailyDouble();

    var category_id = currentQuestion.category;
    var category_name = game.categories[category_id].name;

    $('#dd_area #header_category').html(category_name);
    $('#dd_area #header_value').html(currentQuestion.value);
    $('#dd_area').show('slow');
};


var resetDailyDouble = function() {
    currentDailyDoublePlayer = -1;
    currentDailyDoubleWager = -1;

    $('#dd_area #wager_select').hide();
    $('#dd_area #player_select').show();
};


var displayRegularQuestion = function() {
    resetAnswerArea();

    var category_id = currentQuestion.category;
    var category_name = game.categories[category_id].name;

    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html(currentQuestion.value);
    $('#question_area #question').html(currentQuestion.question);
    $('#question_area #answer').html(currentQuestion.answer);
    $('#question_area').show('slow');
};


var resetAnswerArea = function() {
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


var correct = function(source, player_pk) {
    // Disable further button pushing and mark answer as correct.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('correct');

    var value = (currentQuestion.daily_double) ? currentDailyDoubleWager : currentQuestion.value;
    addResultToCurrentQuestion(player_pk, value);
    finishCurrentQuestion();
};


var incorrect = function(source, player_pk) {
    // Disable further button pushing and mark answer as incorrect.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('wrong');

    var value = (currentQuestion.daily_double) ? currentDailyDoubleWager : currentQuestion.value;
    addResultToCurrentQuestion(player_pk, -value);

    if (currentQuestion.daily_double) {
        finishCurrentQuestion();
    }
};


var addResultToCurrentQuestion = function(player_pk, score_change) {
    currentQuestionNewResult[player_pk] = score_change;
};


var finishCurrentQuestion = function() {
    processCurrentQuestionResults();
    currentQuestion.result = currentQuestionNewResult;
    markCurrentQuestionAsAsked();
    hideAll('slow');
    sendCurrentQuestionToServer();
    resetCurrentQuestion();

    if (allQuestionsHaveBeenAsked()) {
        hideAll();
        $('#proceed_to_final_area').show('slow');
    }
};


var processCurrentQuestionResults = function() {
    for (var player_pk in currentQuestionNewResult) {
        adjustScore(player_pk, currentQuestionNewResult[player_pk]);
    }
};


var adjustScore = function(player_pk, diff) {
    game.players[player_pk].score += diff;
    displayScore(player_pk, game.players[player_pk].score);
};


var displayScore = function(player_pk, score) {
    $('#score_board #score' + player_pk).fadeOut().html(score).fadeIn();
};


var markCurrentQuestionAsAsked = function() {
    currentQuestion.asked = true;
    $(currentQuestionSource).removeClass().addClass('asked_question');
};


var sendCurrentQuestionToServer = function() {
    $.ajax({
        url: '/update_game/' + game.pk + '/',
        type: 'POST',
        data: $.toJSON(currentQuestion),
        error: function() {
            $('#ajax_status').html('failure!').fadeIn().delay(800).fadeOut();
        },
        success: function(data) {
            $('#ajax_status').html('success').fadeIn().delay(800).fadeOut();
        },
        dataType: 'json'
    });
};


var resetCurrentQuestion = function() {
    currentQuestion = null;
    currentQuestionSource = null;
    currentQuestionNewResult = {};
};


var cancelCurrentQuestion = function() {
    hideAll();
    resetCurrentQuestion();
};


var redoAlreadyAskedQuestion = function() {
    undoCurrentQuestionLastResult();
    markCurrentQuestionAsUnasked();
    currentQuestion.result = {};
    sendCurrentQuestionToServer();
    displayCurrentQuestion();
};


var undoCurrentQuestionLastResult = function() {
    for (var player_pk in currentQuestion.result) {
        adjustScore(player_pk, -currentQuestion.result[player_pk]);
    }
};


var markCurrentQuestionAsUnasked = function() {
    currentQuestion.asked = false;
    $(currentQuestionSource).removeClass().addClass('board_question');
};


var nobodyGotIt = function() {
    finishCurrentQuestion();
};


var selectDailyDoublePlayer = function(player_pk) {
    currentDailyDoublePlayer = player_pk;
    displayWagerSelect();
};


var displayWagerSelect = function(player_pk) {
    $('#dd_area #player_select').hide();
    $('#dd_area #wager_select #chosen_player').html(game.players[currentDailyDoublePlayer].username);
    $('#dd_area #wager_select').show();
};


var selectDailyDoubleWager = function(wager) {
    wager = parseInt(wager);
    if (isNaN(wager)) {
        $('#wager_select p.errors').html('That is not a valid wager.');        
    }
    else {
        var curScore = game.players[currentDailyDoublePlayer].score;
        var maxWager = (curScore > 500) ? curScore : 500;
        if (wager > maxWager) {
            $('#wager_select p.errors').html("You can't wager that much.");
        }
        else if (wager < 0) {
            $('#wager_select p.errors').html("Your wager cannot be negative.");
        }
        else {
            $('#wager_select p.errors').html("");
            currentDailyDoubleWager = wager;
            askDailyDoubleQuestion();
        }
    }
};


var askDailyDoubleQuestion = function() {
    $('#answer_area tr:not(#answer_row_' + currentDailyDoublePlayer + ')').hide();
    $('#question_area #nobody').hide();
    hideAll();
    displayRegularQuestion();
};


var allQuestionsHaveBeenAsked = function() {
    for (var i in game.questions) {
        if (!game.questions[i].asked) {
            return false;
        }
    }
    return true;
};


var proceedToFinalJpardy = function() {
    hideAll();

    for (var i in game.players) {
        if (game.players[i].score <= 0) {
            $('#final_wager_area #final_wager_' + i)
                .attr('disabled', 'disabled')
                .val("Sorry, not enough money.");
        }
        else {
            finalJpardyPlayers.push(i);
        }
    }

    $('#final_wager_area h4 span').html(game.final_question.category);
    $('#shadow').show();
    $('#final_wager_area').show();
};


var submitFinalWagers = function() {
    $('#final_wager_area ul').html('');

    var wagers = {};
    var wagersOk = true;

    for (var i in finalJpardyPlayers) {
        var player_pk = finalJpardyPlayers[i];
        var wager = parseInt($('#final_wager_area #final_wager_' + player_pk).val());
        if (isNaN(wager)) {
            $('#final_wager_area ul')
                .append("<li>" + game.players[player_pk].username + "'s wager is invalid.</li>");
            wagersOk = false;
        }
        else {
            var curScore = game.players[player_pk].score;
            if (wager > curScore) {
                $('#final_wager_area ul')
                    .append("<li>" + game.players[player_pk].username + "'s wager is too high.</li>");
                wagersOk = false;
            }
            else if (wager < 0) {
                $('#final_wager_area ul')
                    .append("<li>" + game.players[player_pk].username + "'s wager cannot be negative.</li>");
                wagersOk = false;
            }
            else {
                wagers[player_pk] = wager;
            }
        }
    }

    if (wagersOk) {
        finalJpardyWagers = wagers;        
        displayFinalQuestion();
    }
};


var displayFinalQuestion = function() {
    hideAll();
    resetAnswerRows();

    $('#answer_area tr').hide();
    for (var i in finalJpardyWagers) {
        $('#answer_area #answer_row_' + i)
            .find('.correct_button')
                .attr('onclick', 'finalQuestionCorrect(this, ' + i + ')')
            .end()
            .find('.incorrect_button')
                .attr('onclick', 'finalQuestionIncorrect(this, ' + i + ')')
            .end()
            .show();
    }

    var category_name = game.final_question.category;

    $('#question_area #header_category').html(category_name);
    $('#question_area #header_value').html('final jpardy');
    $('#question_area #question').html(game.final_question.question);
    $('#question_area #answer').html(game.final_question.answer);
    $('#question_area button:not(.correct_button, .incorrect_button)').remove();
    $('#question_area').show('slow');
};


var finalQuestionCorrect = function(source, player_pk) {
    // Disable further button pushing and mark answer as correct.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('correct');

    adjustScore(player_pk, finalJpardyWagers[player_pk]);
};


var finalQuestionIncorrect = function(source, player_pk) {
    // Disable further button pushing and mark answer as incorrect.
    $(source).closest('tr')
        .find('button')
            .attr('disabled', 'disabled')
            .removeClass()
            .addClass('disabled_button')
        .end()
        .find('td:last')
            .text('wrong');

    adjustScore(player_pk, -finalJpardyWagers[player_pk]);
};


$(document).ready(function(){
    $('#question_area').hide();
    $('#already_asked_area').hide();
    $('#dd_area').hide();
    $('#dd_area #wager_select').hide();
    $('#proceed_to_final_area').hide();
    $('#final_wager_area').hide();
    $('#ajax_status').hide();
    $('#shadow').hide();

    if (allQuestionsHaveBeenAsked()) {
        hideAll();
        $('#proceed_to_final_area').show('slow');
    }
});
