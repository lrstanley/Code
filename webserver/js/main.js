
// Use this to trim the text size of channel names for the channel list
Handlebars.registerHelper('trimString', function(passedString, passedLength) {
    if (passedString.length > passedLength) {
        var passedString = passedString.substring(0,passedLength) + '<font color="teal"><b>...</b></font>';
    }
    return new Handlebars.SafeString(passedString);
});

function login() {
    $.get('/', {pass: $('#password').val()})
        .done(function(data) {
            // Set cookie here
            $.cookie('code_pass', $('#password').val(), { expires: 7, path: '/' });
            // Now authed, so hide the password stuff
            $('#modal-password').modal('hide');
            // And show the page
            $('#wrapper').show();
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

$('#modal-password').modal({
    keyboard: false,
    backdrop: 'static',
    show: false
});

$('#modal-timeout').modal({
    keyboard: false,
    backdrop: 'static',
    show: false
});

$('#modal-shutdown').modal({
    keyboard: false,
    backdrop: 'static',
    show: false
});

function doPopulate(isgo) {
    if (isgo) {
        // Initially populate page...
        populate();
        // Populate page every 1.5 seconds. Should be safe..
        updater = setInterval(function(){populate()},1000);
        timeout = setInterval(function(){checkTimeout()},500);
    } else {
        clearInterval(updater)
        clearInterval(timeout)
    };
}

function checkTimeout () {
    var current = new Date().valueOf();
    var diff = current - last_connect;
    if (diff > 15000) {
        $('#modal-timeout').modal('show');
        seconds = Math.round(diff/1000);
        minutes = Math.round(seconds/60);
        if (minutes == 1) {
            $("#timeout").text('1 minute ago');
        } else if (minutes > 1) {
            $("#timeout").text(minutes + ' minutes ago');
        } else {
            $("#timeout").text(seconds + ' seconds ago');
        }
    } else {
        $('#modal-timeout').modal('hide');
    }
}


last_msg_time = 100000;
function populate() {
    $.get('/', $.param({pass: $.cookie('code_pass'), callback: '?'}))
        .done(function(data) {
            code = data;
            // Use this for timeout checking...
            last_connect = new Date().valueOf();
            // Few things, cleanup wise..
            //code['data']['logs'] = code['data']['logs'].splice(-12);
            if (!loginCheck) {
                // Logged in successfully. Do once.
                loginCheck = true;
            };

            // Now, here instead of loading the index.html each time, we actually POPULATE the data on the page...
            //   will be fun!
            if (first_load) {
                first_load = false;
                // Things here will be done on load, AFTER getting data from the API
                // Good for things that won't change in the bot while the webpage is open...
                if (code['data']['muted']) {
                    $("#mute").hide();
                    $("#unmute").show();
                } else {
                    $("#unmute").hide();
                    $("#mute").show();
                };
                $("#server-info").text(code['data']['config']['host'] + ':' + code['data']['config']['port']);
                $("#dashboard-host").text(code['data']['config']['host']);
                $("#default-nick").text(code['data']['config']['nick']);
                // Snap to the bottom of the console log by default
                document.getElementById("chat-bottom").scrollIntoView();
            }
            // Some navbar stuff
            $("#current-nick").text(code['data']['nick']);
            $("#module-count").text(code['data']['modules'].length);
            $("#connection-uptime").text(code['data']['irc_startup'][0]);
            $("#bot-uptime").text(code['data']['bot_startup'][0]);

            // These will throw errors.. but still work oddly enough. Not sure why yet.
            // (The error is saying channel_list_tmpl doesn't exist. If it doesn't exist
            // then how is it being used...)
            $('#channel-list').html(channel_list_tmpl(code));

            // channel list for sending messages
            // Store the old one, so we don't reset the set channel they are about to message..
            old = $('#msg-sender').val();
            $('#msg-sender').html('');
            // Fill the list with new ones
            $.each(code['data']['chan_data'], function(index, value) {
              $('#msg-sender').append('<option>' + index + '</option>');
            });
            if ($.inArray(old, code['data']['chan_data'])) {
                // If the old channel is still in the list, reselect it!
                $('#msg-sender').val(old);
            }
            $('#console-log').html(console_log_tmpl(code));
            jQuery('#console-log').linkify();
            logs = code['data']['logs'];
            if (logs.length > 0) {
                if (logs[logs.length-1]['time'] != last_msg_time) {
                    last_msg_time = logs[logs.length-1]['time'];
                    document.getElementById("chat-bottom").scrollIntoView();
                }
            }
        })
        .fail(function(data) {
            if (!loginCheck) {
                // Cookie has password but it's wrong..
                $.removeCookie('code_pass');
                window.location.href = '/';
            }
        });
    // $.get('/templates/index.html', function(source) {
    //     template = Handlebars.compile(source);
    //     $('#page').html(template(code));
    // });
}

function part(channel) {
    $.get("/", {pass: $.cookie('code_pass'), args: "PART " + channel, data: ""});
    popup("Left " + channel + '!');
}

function mute() {
    $.get("/", {pass: $.cookie('code_pass'), execute: 'mute', data: ""});
    $("#mute").hide();
    $("#unmute").show();
    popup("Muted bot!");
}

function unmute() {
    $.get("/", {pass: $.cookie('code_pass'), execute: 'unmute', data: ""});
    $("#unmute").hide();
    $("#mute").show();
    popup("Unmuted bot!");
}

function sendMessage() {
    if (!$('#msg-sender').val()) {
        $("#msg-input").addClass("has-error");
        return
    }
    if (!$('#msg-text').val()) {
        $("#msg-input").addClass("has-error");
        return
    }
    $.get("/", {pass: $.cookie('code_pass'), args: "PRIVMSG " + $('#msg-sender').val(), data: $('#msg-text').val()});
    // Remove the error assuming it sent
    $("#msg-input").removeClass("has-error");
    console.log($('#msg-sender').val() + ' ... ' + $('#msg-text').val());
    // Snap to bottom when a message is sent
    document.getElementById("chat-bottom").scrollIntoView();
    $('#msg-text').val('');
    $('#msg-text').focus();
}

function join() {
    $.get("/", {pass: $.cookie('code_pass'), args: "JOIN " + $('#join-channel').val(), data: ""});
    $('.modal-join').modal('hide');
    popup("Joined " + $('#join-channel').val() + '!');
    $('#join-channel').val('');

}


function popup(text) {
    $.bootstrapGrowl(text);
}


function exec(method) {
    doPopulate(false);
    $('.modal-shutdown').modal('show');
    $.get("/", {pass: $.cookie('code_pass'), execute: method, data: ""});
}

$("#password-box").keyup(function(event) {
    if (event.keyCode == 13) {
        login();
    }
});

$("#msg-text").keyup(function(event) {
    if (event.keyCode == 13) {
        sendMessage();
    }
});

$("#join-channel").keyup(function(event) {
    if (event.keyCode == 13) {
        join();
    }
});


$(function() {
    first_load = true;
    loginCheck = false;
    if (!$.cookie('code_pass')) {
        // Hide the entire page
        $('#wrapper').hide();
        // Show the password box
        $('#modal-password').modal('show');
    } else {
        // Load content into page here
        $('#wrapper').show();
        doPopulate(true);
    };

    // Preload some templates here, so we don't have to continuously GET them,
    // slowing down the browser and putting more load on the bot
    $.get('/templates/channel_list.html', function(source) {
        channel_list_tmpl = Handlebars.compile(source);
    });
    $.get('/templates/console_log.html', function(source) {
        console_log_tmpl = Handlebars.compile(source);
    });
});

(function($){

  var url1 = /(^|&lt;|\s)(www\..+?\..+?)(\s|&gt;|$)/g,
      url2 = /(^|&lt;|\s)(((https?|ftp):\/\/|mailto:).+?)(\s|&gt;|$)/g,

      linkifyThis = function () {
        var childNodes = this.childNodes,
            i = childNodes.length;
        while(i--)
        {
          var n = childNodes[i];
          if (n.nodeType == 3) {
            var html = $.trim(n.nodeValue);
            if (html)
            {
              html = html.replace(/&/g, '&amp;')
                         .replace(/</g, '&lt;')
                         .replace(/>/g, '&gt;')
                         .replace(url1, '$1<a href="http://$2">$2</a>$3')
                         .replace(url2, '$1<a href="$2">$2</a>$5');
              $(n).after(html).remove();
            }
          }
          else if (n.nodeType == 1  &&  !/^(a|button|textarea)$/i.test(n.tagName)) {
            linkifyThis.call(n);
          }
        }
      };

  $.fn.linkify = function () {
    return this.each(linkifyThis);
  };

})(jQuery);