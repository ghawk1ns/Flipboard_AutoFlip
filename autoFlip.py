__author__ = 'Guy Hawkins'

import urllib
import urlparse
import pickle
import os
import json
import pydoc

from BeautifulSoup import BeautifulSoup
from time import sleep, strftime, localtime
from pyvirtualdisplay import Display
from selenium import webdriver



##################
## URL scrapper ##
##################
class MyOpener(urllib.FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15'

def scrape(url):
    '''
    return a list of urls scraped from the given url

    args:
    url - the url as the string in which we are to use to extract other urls

    returns a list of urls gathered from the given url
    '''
    myOpener = MyOpener()
    page = myOpener.open(url)
    text = page.read()
    page.close()
    soup = BeautifulSoup(text)

    result = []
    for tag in soup.findAll('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href'])
        result.append(str(tag['href']))

    return filter(result)

def filter(ls):
    '''
    filters a list based on a pre-defined criteria

    args:;
    ls - a list

    returns a subset of list
    '''
    #TODO: Implement a filter for scrape
    return ls

##############
## Database ##
##############
'''
    A Pickle database to keep track of urls flipped into magazines
'''
class DB(object):

    def __init__(self, dbName):
        self.dbName = dbName
        self.container = set()
        self.loadDB()

    def __str__(self):
        return str(self.container)

    def saveDB(self):
        with open(self.dbName, 'wb') as f:
            pickle.dump(self.container, f)

    def loadDB(self):
        #check if file exists
        if os.path.isfile(self.dbName):
            #open it
            with open(self.dbName, 'rb') as f:
                # If the file isn't at its end or empty
                if f.tell() != os.fstat(f.fileno()).st_size:
                    self.container = pickle.load(f)

    def add(self, item):
        self.container.add(item)

    def addAndSave(self, item):
        self.container.add(item)
        self.saveDB()

    def contains(self, item):
        return item in self.container

    def getList(self):
        return self.container

###############
## Flipboard ##
###############
def selectMagazines(url, magazines):
    '''
    given a url string and a list of magazine names, determine a subset of magazines from the url string

    args:
    url -- a url string
    magazines -- a list of flipboard magazine names

    returns list which is a subset of magazines, derived in some way by the url string
    '''
    #TODO: determine which magazines url should be flipped into by creating a subset from magazines
    return magazines



def add_url(url, magazines, username, password, vDisplay=False):
    '''
    flips an article into flipboard magazines. Uses Selenium to execute javascript in firefox.

    args:
    url - the url of the article to be flipped
    magazines - a list of flipboard magazine names
    username - the user's login name as a string
    password - the user's password as a string
    vDisplay - flag to determine if we are to use the python virtual display
    '''
    try:
        # Launch virtual display if running in background or from cloud service/server such as digitalocean or heroku
        if vDisplay:
            display = Display()
            display.start()
        #TODO: make browser an init property - giver user a browser choice
        browser = webdriver.Firefox()
        browser.get(url)
        sleep(10)
        # Flip It Tool javascript
        browser.execute_script('''
        javascript: void((function (d, w, p, s, r, t, l) {
            t = (w.screenTop || w.screenY) + 50;
            l = (w.screenX || w.screenLeft) + (w.innerWidth || d.documentElement.offsetWidth || 0) / 2 - s / 2;
            w.__flipboard = w.open('https://share.flipboard.com/bookmarklet/popout?v=2&title=' + encodeURIComponent(d.title) + '&url=' + encodeURIComponent(w.location.href) + '&t=' + p, '__flipboard_flipit', 'width=' + s + ',height=' + r + ',top=' + t + ',left=' + l + ',location=yes,resizable=yes,status=no,scrollbars=no,personalbar=no,toolbar=no,menubar=no');
            s = d.createElement('script');
            s.setAttribute('type', 'text/javascript');
            s.setAttribute('src', 'https://d2jsycj2ly2vqh.cloudfront.net/bookmarklet/js/popout-helper.min.js?t=' + p);
            d.body.appendChild(s);
            setTimeout(function () {
                w.__flipboard.focus()
            }, 50);
        })(document, window, (new Date().getTime()), 535, 565))
        '''
        )
        sleep(5)
        #Here we need to switch to the new window opened by the javascript.
        browser.switch_to_window(browser.window_handles[1])
        user_field = browser.find_element_by_name('username')
        password_field = browser.find_element_by_name('password')
        submit = browser.find_element_by_xpath('//*[@class="flbutton done left"]')
        user_field.send_keys(username)
        password_field.send_keys(password)
        submit.click()
        sleep(15)# Give plenty of time to load
        # Find magazines on web
        allMagazines = browser.find_elements_by_xpath('//h1[@class="magazine-title ng-binding"]')
        # select which magazine to add this too
        selectedMagazines = selectMagazines(url, magazines)
        addToMagazines = False
        magCount = 0
        for mag in allMagazines:
            if mag.text in selectedMagazines:
                log('Adding to: ' + mag.text, indent=True, extraLine=False, time=False)
                mag.click()
                magCount += 1
        if magCount > 0:
            if magCount != len(selectedMagazines):
                log('Could not flip into all selected magazines flipped ' + magCount + ' of ' + len(selectedMagazines), indent=True, extraLine=False, time=False)
            else:
                log('Flipped into all selected magazines', indent=True, extraLine=False, time=False)
            # submit
            add = browser.find_element_by_xpath('//*[@class="btn right"]')
            add.click()
            # ensure it processes
            sleep(.5)
        else:
            log('Could not flip: ' + mag.text, indent=True, extraLine=False, time=False)
            log('\tselectedMagazines: ' + selectedMagazines, indent=True, extraLine=False, time=False)
            log('\tallMagazines ' + allMagazines, indent=True, extraLine=False, time=False)
    except Exception, e:
        log('An error has occurred while trying to flip url into selected magazines', indent=False, extraLine=False, time=True)
        log(e.message, indent=False, extraLine=False, time=True)
    finally:
        log("Stopping browser", indent=True, extraLine=False, time=False)
        browser.quit()
        if vDisplay:
            log("Stopping display", indent=True, extraLine=False, time=False)
            display.stop()

#######################################################################################
#######################################################################################
#######################################################################################
## Main Functions ##
####################
def getTime():
    '''Returns the local time as a string'''
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

def log(report, indent=False, extraLine=False, time=True):
    '''Generates a log by saving to log.txt and outputting to command line

    parameters:
    report -- a string containing the message to log
    indent -- flag to determine if line should be indented (default False)
    extraLine -- flag to determine if an extra line should be appended to current line (default False)
    time -- flag to determine if time should be appended to start of line (default true)'''
    print report
    final = ''
    if indent:
        final = '\t'
    if time:
        final += strftime("%Y-%m-%d %H:%M:%S", localtime())+': '
    else:
        final += '> '
    final += report+'\n'
    if extraLine:
        final += '\n'
    with open("log.txt", "a") as log:
            log.write(final)


'''
    Gets login info from login.properties file
'''
def init():
    '''
    reads the json login.properties and init.properties in. These determine the system and login properties

    returns:
    a dictionary containing the key-value results
    '''
    try:
        #get the login credentials
        with open("login.properties", "r") as file:
            data = json.load(file)
        #get the rest of the properties
        with open("init.properties", "r") as file:
            data.update(json.load(file))
    except Exception, e:
        print 'Initialization error: ' + e.message
        exit(-1)
    return data

def assert_property(prop, expectedType):
    '''
    Assert properties were read in correctly from init()

    arguments:
    prop -- some properties variable
    expectedType -- the expected type of prop
    '''
    assert type(prop) is expectedType

    if expectedType is str:
        assert len(prop) > 0

    if expectedType is list:
        pass

    if expectedType is bool:
        pass

def main():
    '''
    The main function of autoFlip. Call this to start the service.
    '''
    #######################
    ## Initialize project ##
    #######################
    properties = init()
    # check and set properties
    username = str(properties["username"])
    assert_property(username, str)
    # flipboard password
    password = str(properties["password"])
    assert_property(password, str)
    # name of Pickle DB
    dbName = str(properties["database"])
    assert_property(dbName, str)
    # list of websites to poll
    websites = properties["websites"]
    assert_property(websites, list)
    # list of magazines to read from
    magazines = properties["magazines"]
    assert_property(magazines, list)
    #If virtual display is needed (good for heroku / cloud / servers
    vDisplay = properties["vDisplay"]
    assert_property(vDisplay, bool)
    # The minutes to sleep in-between checks
    sleepIntervalMinutes = properties["sleepIntervalMinutes"]
    assert_property(sleepIntervalMinutes, int)

    # add new properties as needed
    # ...

    #load Pickle database
    db = DB(dbName)
    ################################################
    ## Runner ##
    ############
    # count keeps track of each iteration
    count = 0
    while True:
        count += 1
        for website in websites:
            log("Polling for urls: " + str(count), indent=False, extraLine=False, time=True)
            # get urls from website
            urls = scrape(website)
            log("found " + str(len(urls)) + " urls", indent=True, extraLine=False, time=False)
            for url in urls:
                # make sure we have not already added this url to our magazines
                if not db.contains(url):
                    log("Attempting to add " + url, indent=True, extraLine=False, time=False)
                    # attempt to add the url to the magazines
                    add_url(url, magazines, username, password, vDisplay)
                    sleep(3)
                    db.addAndSave(url)
                    sleep(3)
            log("Complete", indent=True, extraLine=False, time=False)
        # check every 10 mins
        sleep(600)