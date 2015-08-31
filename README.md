# Code the flexible Python IRC Bot

Code is a open source python IRC bot. Code can run on any operating system that supports Python 2.7, but works best on Linux based distrobutions.

Feel free to test Code here: http://byteirc.org/channel/L

## Features

Code is packed full of features ranging from raw IRC functions to modules that can be unloaded and loaded with ease. Some features include:

#### Control panel
Code has a built-in control panel that you can enable, that also serves as a webserver and a REST api that allows you to remotely execute functions or retrieve information from the bot, all via GET/POST requests. Everything authenticated too!

#### The control panel itself:
![The control panel](http://i.imgur.com/ewAgVNu.png)

Webserver authentication:
![Control panel authentication](http://i.imgur.com/w5kbij3.png)

Mute feature (also shutdown, reboot, etc):
![Control panel muting](http://i.imgur.com/BAkdmw0.png)

#### Fast & lightweight
Code is very small, so even with the extensive amount of features it has, it should run as little as possible.

#### Modules
Code uses modules for all of its commands and features. These modules can be loaded, unload, completely removed, and dynamically updated to fit the channels needs. Modules can be made easily, and because of the nature of the modules, you can make whatever you want/control the bot easily.

#### Very user friendly
It is very easy to install and run Code, even if you have no knowledge of ever running a IRC bot before. I created the bot so it has either no external modules, or the modules are packaged with it. Help commands also help you with specific documentation for almost every command. Try `.help <command>`

#### Easy to use API
When creating your own modules, it is always very easy to have a documented API and easy to understand functions. Note, the API isn't fully documented, so there are a lot of features that aren't listed there. See the [Wiki](https://github.com/Liamraystanley/Code/wiki) for more information.

#### Open-Source
Found a bug, feature, or need technical support/advice? You can always navigate to the [Github](https://github.com/Liamraystanley/Code/issues) page to make requests and post bugs. Heck, even fork Code and make your own modifications!

#### Configuration
Almost ever single aspect of the bot is configurable to your likings. Don't like a module? Remove it. Like only ONE module? Whitelist it!

## Installation - How do I install? 

**If you have any issues during the install, feel free to head to http://chat.liamstanley.io/ to get help**

Unix & Unix-like OS: 
--------------------

    apt-get install python2.7 git screen
    git clone https://github.com/Liamraystanley/Code.git
    cp -rf example.json config.json
    nano config.json
    python code.py

If you wish to not run your bot in the foreground, you may use the `screen` daemon as so:

    screen -S code python code.py

This creates a terminal window that can be logged into and out without disturbing the process in that window. To exit screen safely, hit `CTRL+A` then `CTRL+D`.
To log back into, and view the playback of Code, type `screen -x code`.

Windows: 
--------------------


- Make sure you have Python installed `http://www.python.org/download/releases/2.7.5/`
- Download Code here: `https://github.com/Liamraystanley/Code/zipball/master` and unzip it.
- Copy and rename `example.json` to `config.json` (Note, it's best NOT to use the Windows notepad, rather, use Notepad++)
- You can open up command prompt, `cd` to Codes directory, and execute Code with `python code.py`.
- Note, if command prompt says that `python` is not a internal or external command/program, that means Python failed to be added to your system-wide %PATH% file. So, you need to add it to the %PATH% variable.

Licensing
---------
_________

Code Copyright (C) 2012-2015 Liam Stanley
    `Eiffel Forum License, version 2`
    
    1. Permission is hereby granted to use, copy, modify and/or
        distribute this package, provided that:
            * copyright notices are retained unchanged,
            * any distribution of this package, whether modified or not,
              includes this license text.
    2. Permission is hereby also granted to distribute binary programs
        which depend on this package. If the binary program depends on a
        modified version of this package, you are encouraged to publicly
        release the modified version of this package.
    
    THIS PACKAGE IS PROVIDED "AS IS" AND WITHOUT WARRANTY. ANY EXPRESS OR
    IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE AUTHORS BE LIABLE TO ANY PARTY FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES ARISING IN ANY WAY OUT OF THE USE OF THIS PACKAGE.
