var app = angular.module('main', []);
var last_msg = 0;

function scrollToView(el) {
    $(el).animate({ scrollTop: $(el)[0].scrollHeight}, 250);
}

function popup(text) {
    $.bootstrapGrowl(text, {
      ele: 'body', // which element to append to
      type: 'success', // (null, 'info', 'danger', 'success')
      offset: {from: 'bottom', amount: 20}, // 'top', or 'bottom'
      align: 'right', // ('left', 'right', or 'center')
      width: 250, // (integer, or 'auto')
      delay: 3000,
      allow_dismiss: true,
    });
}

app.controller('mainCtrl', function($scope, $interval, $http) {
    $scope.logs = "";
    $scope.api = "";
    // Internal failure counter for api requests.
    $scope.failed = 0;
    // Used to tally up successful queries, so we know when
    // we're "really" connected
    $scope.success = 0;
    // Used for generic errors, like internet conn. issues
    $scope.error = false;
    // Used when the bot restarts
    $scope.restarting = false;
    // Used when the bot quits
    $scope.quit = false;

    $scope.$watch('failed', function() {
        // Watch for failed logins. After 10 exceptions, something is for sure
        // broken.
        if ($scope.failed > 10 && !$scope.restarting && !$scope.quit) {
            $scope.error = true;
            $scope.success = false;
            $scope.api = false;
        }
    });

    $scope.$watch('success', function() {
        // Check to see how many successful queries there have been.
        // If over 5, we're assuming the connection has resumed after disconnect
        $scope.failed = 0;
        if ($scope.success > 5) {
            $scope.error = false;
            $scope.restarting = false;
        }
    })

    $scope.sendmessage = function() {
        if (!$scope.chatchannel || !$scope.chatbox) {
            return;
        }
        data = {
            args: "PRIVMSG " + $scope.chatchannel,
            data: $scope.chatbox
        }
        $http.post("/exec", data).success(function() {
            $scope.chatbox = "";
            update_logs();
        })
        $("#msg-text").focus();
    }

    $scope.mute = function() {
        // Mute the bot
        $http.get("/exec/mute").success(function(response) {
            $scope.api.muted = response.muted;
            if (response.muted) { popup("Successfully muted."); }
        });
    }

    $scope.unmute = function() {
        // Unmute the bot
        $http.get("/exec/unmute").success(function(response) {
            $scope.api.muted = response.muted;
            if (!response.muted) { popup("Successfully unmuted."); }
        });
    }

    $scope.join_channel = function() {
        if ($scope.joinbox.substr(0,1) != "#") {
            $scope.joinbox = "#" + $scope.joinbox
        }

        data = {
            args: "JOIN " + $scope.joinbox
        }

        $http.post("/exec", data).success(function(response) {
            if (response.success) {
                popup("Attempting to join " + $scope.joinbox);
                $scope.joinbox = "";
                $timeout(update_page, 1000);
            }
        })
    }

    $scope.part_channel = function(name) {
        data = {
            args: "PART " + name
        }

        $http.post("/exec", data).success(function(response) {
            if (response.success) {
                update_page();
                popup("Left " + name);
            }
        })
    }

    $scope.reloadall = function() {
        $http.get("/exec/reload").success(function(response) {
            if (response.reload) { popup("Reloaded all modules."); }
        })
    }

    $scope.reload = function(name) {
        $http.get("/exec/reload/" + name).success(function(response) {
            if (response.reload) { popup("Reloaded " + name); }
        })
    }

    $scope.mod_unload = function(name) {
        $http.get("/exec/unload/" + name).success(function(response) {
            if (response.success) {
                popup("Unloaded " + name);
                update_page();
            } else {
                popup(response.message);
            }
        })
    }

    $scope.mod_load = function() {
        $http.get("/exec/load/" + $scope.loadbox).success(function(response) {
            if (response.success) {
                popup("Loaded " + name);
                $scope.loadbox = "";
                update_page();
            } else {
                popup(response.message);
            }
        })
    }

    $scope.restart = function() {
        // Restart the bot. Wait for connections to flow through again.
        $http.get("/exec/restart");
        $scope.success = 0;
        $scope.api = false;
        $scope.restarting = true;
    }

    $scope.shutdown = function() {
        // Shutdown the bot and disable our queries
        $http.get("/exec/shutdown");
        $scope.success = 0;
        $scope.quit = true;
        $scope.api = false;
    }

    var update_page = function() {
        // Update misc things on the page, at slower rate.
        if ($scope.quit) { return; }
        $http.get("/api/config,server,nick,modules,channels,bot_startup,muted").success(function(response) {
            $scope.api = response;
            $scope.failed = 0;
        });
    }

    var update_logs = function() {
        // Update logs. Updates faster because most important thing.
        if ($scope.quit) { return; }
        $http.get("/api/logs").success(function(response) {
            if (!response.logs) {
                $scope.failed = ++$scope.failed;
                return;
            }
            if ($scope.logs.toString() === response.logs.toString()) {
                var shouldScroll = false;
            } else {
                var shouldScroll = true;
            }
            $scope.logs = response.logs;
            if (shouldScroll) {
                scrollToView("#channel-log");
            }
            $scope.failed = 0;
            $scope.success = ++$scope.success;
        }).error(function() {
            $scope.failed = ++$scope.failed;
        });
    }

    // Initially update the page, as $interval does it the first time AFTER
    // the initial interval hits
    update_page();
    update_logs();
    $interval(update_page, 4000);
    $interval(update_logs, 1000);
    // Snap chat into view, it doesn't handle well on page load
    setTimeout(function(){
        scrollToView("#channel-log");
    }, 250);
});

app.controller('loginCtrl', function($scope, $http) {
    $scope.passwd = "";
    $scope.login = function() {
        if (!$scope.passwd) { return; }
        data = {
            passwd: $scope.passwd
        }
        $http.post("/login", data).success(function(response) {
            if (!response.success) {
                $scope.error = true;
                $scope.passwd = "";
                $("#inputPassword").focus();
            } else {
                $scope.error = false;
                window.location.replace("/");
            }
        });
    }

    $scope.$watch('passwd', function() {
        if ($scope.passwd.length > 0) {
            $scope.error = false;
        }
    })
});


function isElementInViewport(el) {

    //special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) && /*or $(window).height() */
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) /*or $(window).width() */
    );
}