function login() {
    $.get('/', {pass: $('#password').val()})
        .done(function(data) {
            // Set cookie here
            $.cookie('code_pass', $('#password').val(), { expires: 7, path: '/' });
            $('.modal-password').modal('hide');
            doPopulate(true);
        })
        .fail(function(data) {
            $('#password-text').html(
                'Code - Python IRC Bot<br><font color="red" size="3">Incorrect password</font><br>'
            );
            $("#password-box").addClass("has-error");
            $("#password").val('');
            $("#password").focus();
        });
}

function logout() {
    $.removeCookie('code_pass');
}

$('.modal-password').modal({
    keyboard: false,
    backdrop: 'static',
    show: false
});

$('.modal-shutdown').modal({
    keyboard: false,
    backdrop: 'static',
    show: false
});

$('.modal-chat').modal({
    show: false
});

$('.modal-join').modal({
    show: false
});

function doPopulate(isgo) {
    if (isgo) {
        // Initially populate page...
        populate();
        // Populate page every 1.5 seconds. Should be safe..
        updater = setInterval(function(){populate()},1500);
        //focuser = setInterval(function(){inputFocus("#chat-input")},1);
    } else {
        clearInterval(updater)
    };
}

function populate() {
    $.get('/', $.param({pass: $.cookie('code_pass'), callback: '?'}))
        .done(function(data) {
            code = data;
            // Few things, cleanup wise..
            code['data']['logs'] = code['data']['logs'].splice(-12);
            if (!loginCheck) {
                // Logged in successfully. Do once.
                loginCheck = true;
            };
        })
        .fail(function(data) {
            if (!loginCheck) {
                // Cookie has password but it's wrong..
                $.removeCookie('code_pass');
                window.location.href = '/';
            }
        });
    $.get('/templates/' + name, function(source) {
        template = Handlebars.compile(source);
        $('#page').html(template(code));
    });
}

function part(channel) {
    // &args=PRIVMSG+%23L&data=Testing+123
    $.get("/", {pass: $.cookie('code_pass'), args: "PART " + channel, data: ""});

}

function sendMessage() {
    // &args=PRIVMSG+%23L&data=Testing+123
    $.get("/", {pass: $.cookie('code_pass'), args: "PRIVMSG " + $('#msg-sender').val(), data: $('#msg-text').val()});
    $('.modal-chat').modal('hide');

}

function join() {
    // &args=PRIVMSG+%23L&data=Testing+123
    $.get("/", {pass: $.cookie('code_pass'), args: "JOIN " + $('#join-channel').val(), data: ""});
    $('.modal-join').modal('hide');

}

function exec(method) {
    doPopulate(false);
    $('.modal-shutdown').modal('show');
    $.get("/", {pass: $.cookie('code_pass'), execute: method, data: ""});
}

$("#password-box").keyup(function(event){
    if(event.keyCode == 13){
        login();
    }
});


$(function() {
    loginCheck = false;
    if (!$.cookie('code_pass')) {
        $('.modal-password').modal('show');
    } else {
        // Load content into page here
        doPopulate(true);
    };
});