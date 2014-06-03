function login() {
    $.get('/', {pass: $('#password').val()})
        .done(function(data) {
             // Set cookie here
             // $.cookie('code_pass', $('#password').val(), { expires: 7, path: '/' });
             $('.modal-password').modal('hide');
             populate();
        })
        .fail(function(data) {
             $('#password-text').text('Incorrect password');
             $("#password-box").addClass("has-error");
        });
}

$('.modal-password').modal({
    keyboard: false,
    backdrop: 'static'
});

function populate() {
    // $.cookie('code_pass')
    $.get('/', $.param({pass: 'standerp', callback: '?'}))
        .done(function(data) {
            code = data;
        });
    $.get('/templates/' + name, function(source) {
        template = Handlebars.compile(source);
        $('#page').html(template(code));
    });
}

$("#password-box").keyup(function(event){
    if(event.keyCode == 13){
        login();
    }
});

$(function(){
    if (!$.cookie('code_pass')) {
        $('.modal-password').modal('show');
    } else {
        alert('Successfully logged in...');
        // Load content into page here
    }
});
