Code the flexible Python IRC Bot
================================

Code (on #L @ irc.esper.net) is a open source python IRC bot. Code can run on any operating system that supports Python 2.7.

Features
-------- 
________

Code is packed full of features ranging from raw IRC functions to modules that can be unloaded and loaded with ease. Some features include:

Fast & light weight
- Code is very small, so it won't take up resources.

Load & unload modules
- Code has the ability to load user defined IRC modules, that are pre-made or ones that you create. Code also can live-reload modules for active and fast development.

Very user friendly
- It is very easy to install and run Code, even if you have no knowledge of ever running a IRC bot before. Help commands also help you with specific documentation for almost every command.

Easy to use API
- When creating your own modules, it is always very easy to have a fully documented API and easy to understand functions. See the [Wiki](https://github.com/Liamraystanley/Code/wiki)

Open-Source
- Found a bug, feature, or technical support/advice? You can always navigate to the [Github](https://github.com/Liamraystanley/Code/issues) page to make requests and post bugs. Heck, even fork Code and make your own modifications!

Configuration
- Almost ever single aspect of the bot is configurable to your likings. Don't like a module? Remove it. Like only ONE module? Whitelist it!

Installation - How do I install? 
================================
________________________________

**If you have any issues during the install, feel free to head to http://chat.liamstanley.io/ to get help**


Unix & Unix-like OS: 
--------------------

    apt-get install python2.7 git screen
    git clone https://github.com/Liamraystanley/Code.git
    cp -rf example.json config.json
    nano config.json
    python code.py

If you wish to not run your bot in the forground, you may use the `screen` daemon as so:

    screen -S code python code.py

This creates a terminal window that can be logged into and out without disturbing the process in that window. To exit screen safely, hit `CTRL+A` then `CTRL+D`.
To log back into, and view the playback of Code, type `screen -x code`.


Windows: 
--------------------


    1) Make sure you have Python installed `http://www.python.org/download/releases/2.7.5/`
    2) Download Code here: `https://github.com/Liamraystanley/Code/zipball/master` and unzip it.
    3) Configure Code's configuration file, located in the bot directory.
       - Copy and rename `example.json` to `config.json`
       - Note, it's best NOT to use the Windows notepad, rather, use Notepad++.
    3) You can open up command prompt, `cd` to Codes directory, and execute Code with `python code.py`.
       - Note, if command prompt says that `python` is not a internal or external command/program,
         that means Python failed to be added to your system-wide %PATH% file.
         So, you need to add it to the %PATH% variable.

Licensing
---------
_________

Code Copyright (C) 2012-2014 Liam Stanley
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
