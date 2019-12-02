#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = ["Tuan Nguyen"]
__copyright__ = "Copyright 2018, Tuan Nguyen"
__credits__ = ["Tuan Nguyen"]
__license__ = "GPL"
__version__ = "1.0"
__status__ = "Production"
__author__ = "TuanNguyen"
__email__ = "etuannv@gmail.com"
__website__ = "https://webscrapingbox.com"


# Start import other
from base import *
from urllib.parse import urljoin


def clickPlay():
    # Play to show duration
    tag = browser.findByXpath(".//*[@id='videotube_html5_api']")
    browser.clickElement(tag)

def checkIfPlay():
    logging.info("Checking is playing")
    time.sleep(5)
    
    # Get duration 1
    duration1 = browser.findByXpath(".//span[@class='vjs-remaining-time-display']")
    if duration1:
        duration1 = duration1.get_attribute("innerHtml")

    time.sleep(2)

    # Get duration 2
    duration2 = browser.findByXpath(".//span[@class='vjs-remaining-time-display']")
    if  duration2:
        duration2 = duration2.get_attribute("innerHtml")

    if duration1 and duration2 and duration1 in duration2:
        logging.info("Video is pause. Click play")
        clickPlay()
        return
    
    logging.info("Video is playing")
    

def countdown(t):
    counter = 2
    while t:
        if counter < 0:
            break
        # Wait for duration and play next video
        logging.info("Video duration: {} secs".format(t))
        time.sleep(1)
        t -= 1
        if t == 1:
            time.sleep(2)
            # Get duration
            du = browser.findByXpath(".//span[@class='vjs-remaining-time-display']")
            
            # count number of get
            if not du:
                counter -= 1
                continue
            du = du.get_attribute('innerHTML')
            if '0:00' in du:
                return
            
        if t%20 == 0:
            # Check duration
            # Pause to show duration
            logging.info("Checking duration")
            tag = browser.findByXpath(".//*[@id='videotube_html5_api']")
            browser.clickElement(tag)
            time.sleep(1)
            # Play to show duration
            tag = browser.findByXpath(".//*[@id='videotube_html5_api']")
            browser.clickElement(tag)

            # Get duration
            du = browser.findByXpath(".//span[@class='vjs-remaining-time-display']")
            
            # count number of get
            if not du:
                counter -= 1
                continue
            
            du = du.get_attribute('innerHTML')

            # count number of get
            if not du:
                counter -= 1
                continue
            
            counter = 2
            t = get_sec(du)




            

def isPlayed(url):
    content = {}
    url = url.lower().replace('.html', '')
    url = url.strip('/')
    if os.path.isfile('old.txt'):
        with open('old.txt') as f:
            content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [x.strip() for x in content]

    if not url in content:
        with open("old.txt","a") as f:
            f.write(url + '\n')
        return False
    return True

def playNextVideo(tags, durations):
    for tag, duration in zip(tags, durations):
        url = tag.get_attribute('href')
        video_url = urljoin("https://bit.tube", url)
        if isPlayed(video_url):
            continue
        video_duration = duration.text
        if video_duration:
            video_duration.strip()
            video_duration = get_sec(video_duration)
        logging.info("Play video: {}".format(url))
        browser.clickElement(tag)
        time.sleep(5)

        # Check if video is not play then click paly
        # tag = browser.findByXpath(".//*[@id='videotube_html5_api']")
        # browser.clickElement(tag)
        checkIfPlay()

        logging.info("Video duration: {}".format(video_duration))
        return video_duration

def get_sec(time_str):
    time_str = time_str.replace('-','')
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

def doLogin():
    
    browser.getUrl("https://mobile.twitter.com/login")
    time.sleep(1)

    logging.info("Load cookie")
    browser.loadCookie(CookiePath)

    browser.getUrl("https://mobile.twitter.com/login")

    time.sleep(2)
    
    if browser.isExistByXPath(".//button[contains(text(),'Log in')]",2) or '/login' in browser.getCurrentUrl():
        logging.info("Login to system")
        # browser.getUrl("https://bit.tube/login")
        # Check if loggin then do loggin
        if '/login' in browser.getCurrentUrl() or browser.isExistByXPath(".//button[contains(text(),'Log in')]",2):
            # uname = browser.findByXpath(".//*[@id='page-container']//form//input[@type='text']")
            uname = browser.findByXpath(".//input[contains(@placeholder,'email')]")
            if uname:
                uname.send_keys("miraclepython")
                passwd = browser.findByXpath(".//input[contains(@placeholder,'Password')]")
                # passwd = browser.findByXpath(".//*[@id='page-container']//form//input[@type='password']")
                if passwd:
                    passwd.send_keys("testing12")
                    passwd.submit()
                time.sleep(2)
        
        # Check if is loggin
        while '/login' in browser.getCurrentUrl() or browser.isExistByXPath(".//button[contains(text(),'Log in')]",2):
            time.sleep(3)
            print("Plz login the system ...")

    else:
        logging.info("User is logged")
    
    # Save login cookie
    logging.info("Save cookie")
    browser.saveCookie(CookiePath)
    return True

def followUser(username):
    username = username.replace("@",'')
    url = urljoin("https://twitter.com", username)
    # print("Following: {} ...".format(url))
    browser.getUrl(url)
    # Check if log
    while browser.isExistByXPath(".//a[@href='/login']"):
        doLogin()
        browser.getUrl(url)

    currentUrl = browser.getCurrentUrl()
    pageSource = browser.getPageSource()
    if 'account/suspended' in currentUrl or 'Account suspended' in pageSource:
        logging.info("{} is suspended !".format(username))
        return False
    
    
    if "This account doesn’t exist" in pageSource:
        logging.info("{} doesn't exist !".format(username))
        return False
    
    xpath = ".//a[contains(@href,'{}/photo')]/following::div[1]//div[contains(@data-testid,'-follow')]".format(username)
    # tag = browser.findByXpath(".//input[@type='submit' and @value='Follow']", 3)
    tag = browser.findByXpath(xpath, 3)
    if tag:
        browser.clickElement(tag)
        logging.info("{} is followed".format(username))
        return True
        # elif:
        #     tag = browser.findByXpath(".//div[@class='ProfileNav']//span[text()='Following']/parent::button")
    else:
        logging.info("{} could not be followed".format(username))
        return False
        

    

def main(argv):
    global browser, CurrentPath, TempPath, ConfigPath, CookiePath, DoneFile
    # CurrentPath = os.path.dirname(os.path.realpath(__file__))
    CurrentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    ConfigPath = os.path.join(CurrentPath, 'config.ini')
    TempPath = os.path.join(CurrentPath, 'temp')
    DoneFile = os.path.join(CurrentPath, 'done.txt')
    CookiePath = os.path.join(CurrentPath, 'cookies.pkl')
    browser = None
    
    print('==================== TWITTER AUTO FOLLOW ====================')

    browser = WebBrowser(timeout = 10, isDisableImage = False, currentPath=CurrentPath,  isDisableJavascript = False, changeProxyTotal=50)
    
    # doLogin()


    # Read csv file for users that need to be follow
    list_data = readCsvToList("followers.csv")
    done_data = readTextFileToList(DoneFile)
    counter = 0
    for user in list_data:
        username = user[0]
        # Check if done user
        if username in done_data:
            print("{} is processed".format(username))
            continue

        result = followUser(username)
        writeListToTextFile([username], DoneFile)
        if result:
            time.sleep(150)
        counter +=1

    

    browser.exitDriver()


if __name__ == "__main__":
    main(sys.argv)
    print("\n\n")
    logging.info("DONE !!! etuannv@gmail.com ;)")