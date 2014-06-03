Code the flexible Python IRC Bot
================================

Build State: [![Build Status](https://travis-ci.org/Liamraystanley/Code.png?branch=master)](https://travis-ci.org/Liamraystanley/Code)

Code (on #L @ irc.esper.net) is a open source python IRC bot forked from Phenny/Jenni, with new modules, easier to understand commands, and easy installation! Code can run on any operating system that supports Python 2.7 or higher.

Features
-------- 
________

Code is packed full of features ranging from raw IRC functions to modules that can be unloaded and loaded with ease. Some features include:

Fast & Light Weight
- Code is very small, so it won't take up resources. Also, Code is very responsive and quick-paced! Also he can run in 1-2 processes!

Load & Unload Modules
- Code has the ability to load user defined IRC modules, that are pre-made or ones that you create. Code also can live-reload modules for active and fast development.

Very User Friendly
- It is very easy to install and run Code, even if you have no knowledge of ever running a IRC bot before. ".help" commands, and friendly responses help everything feel smooth and elegant.

Easy-To-use API
- When creating your own modules, it is always very easy to have a fully documented API and easy to understand functions.

Open-Source
- Found a bug, feature, or technical support/advice? You can always navigate to the [Github](https://github.com/Liamraystanley/Code) page to make requests and post bugs. Heck, even fork Code as your own and make your own modifications!

Configuration
- By default, Code has the ability to change his username (including NickServ Authentication), server (including server password), and excluded channel/modules, and more.

Installation - How do I install? 
================================
________________________________

**If you have any issues during the install, feel free to head to http://chat.liamstanley.io/ to get help**


Unix & Unix-like OS: 
--------------------

    1) Make sure you have Python installed `http://www.python.org/download/releases/2.7.5/`
    2) Run `git clone https://github.com/Liamraystanley/Code.git`
       - if you do not have git installed, simply install it via your package manager.
         e.i, `sudo apt-get install git`
    3) rename the `example.json` configuration file to `config.json` (`cp -rf example.json config.json`)
    4) Edit `config.json`
    5) Run `./code` - this now runs code with your settings 

Full command would be: 

    python code

If you wish to run Code on a UNIX shell, the best thing to do would be to fork it to the background process using screen. You do this by execution python/Code with:

    screen -S code ./code

This creates a terminal window that can be logged into and out without disturbing the process in that window. to exit screen safely, hit `CTRL+A` then `CTRL+D`.
To log back into, and view the playback of Code, type `screen -x code`.


Windows: 
--------------------


    1) Make sure you have Python installed `http://www.python.org/download/releases/2.7.5/`
    2) Download Code here: `https://github.com/Liamraystanley/Code/zipball/master` and unzip it.
    3) Configure Code's configuration file, located in the bot directory.
       - Copy and rename `example.json` to `config.json`
       - Note, notepad is not prefered. If anything, use Notepad++ under Windows.
    3) You can open up command prompt, `cd` to Codes directory, and execute Code with `python code`.
       - Note, if command prompt says that `python` is not a internal or external command/program,
         that means Python failed to be added to your system-wide %PATH% file.
         So, you need to add it to the %PATH% variable.
         Feel free to google that one, Code is not COMPLETELY noob-friendly.


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
