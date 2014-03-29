======================
= Flipboard_AutoFlip =
======================
Author: Guy Hawkins
Last Edited: 3/29/2014
----------------------

A service to aggregate links from the pages of websites and and conditionally flip them into selected magazines

###############################
## Required Python Libraries ##
###############################

1. urllib
2. urlparse
3. pickle
4. os
5. json
5. BeautifulSoup
6. time
7. pyvirtualdisplay
8. selenium

######################
## Properties Files ##
######################
JSON format

    # login.properties
        {
            "username" : "AaronRamsey",
            "password" : "Arsenal#1"
        }

    # init.properties
        {
            "sleepIntervalMinutes" : Interval between polling websites for urls
            "database" : "the name of the pickle db, no setup required just choose a name
            "browser" : browser for selenium to launch - leave blank for Firefox
            "vDisplay" : flag for selecting whether or not to use a virtual display - good for servers/heroku/background jobs/ etc
            "websites" :  a list of websites to gather urls from
            "magazines": a list of your flipboard magazines
        }