#!/usr/bin/env python
"""Python-Pinboard

Python script for syncronizing Hacker News <http://news.ycombinator.com> saved stories to Pinboard <http://pinboard.in/> via its API.

Originally written on Pythonista on iPad
"""

__version__ = "1.1"
__license__ = "BSD"
__copyright__ = "Copyright 2013-2014, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/>"

import re
import sys
import urllib
import urlparse
from bs4 import BeautifulSoup
import requests
from types import *
import xml.etree.ElementTree as xml

HACKERNEWS = 'https://news.ycombinator.com'

def getSavedStories(session, hnuser):
    print "...get saved stories..."
    savedStories = {}
    saved = session.get(HACKERNEWS + '/saved?id=' + hnuser)

    soup = BeautifulSoup(saved.content)

    for tag in soup.findAll('td',attrs={'class':'title'}):

        if type(tag.a) is not NoneType:
            try:
                _href = tag.a['href']
                if not str.startswith(str(_href), '/x?fnid'): # skip the 'More' link
                    _href = HACKERNEWS+_href if str.startswith(str(_href), 'item?') else _href
                    savedStories[_href] = tag.a.text
            except:
                print "The saved story has no link, skipping"
    return savedStories

def loginToHackerNews(username, password):
    s = requests.Session() # init a session (use cookies across requests)

    headers = { # we need to specify an header to get the right cookie
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',
        'Accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    loginPage = s.get(HACKERNEWS + '/newslogin', headers=headers)

    soup = BeautifulSoup(loginPage.content)
    inputTag = soup.find(attrs={"name": "fnid"})
    fnid = inputTag['value']

    # Build the login POST data and make the login request.
    payload = {
        'fnid': fnid,
        'u': username,
        'p': password
    }
    auth = s.post(HACKERNEWS+'/y', data=payload, headers=headers )

    if 'Bad login' in str(auth.content):
        raise Exception("Hacker News authentication failed!")
    if not username in str(auth.content):
        raise Exception("Hacker News didn't succeed, username not displayed.")

    return s # return the http session

def postToPinboard(token, url, title):

    payload = {
        'auth_token':token,
        'url': url,
        'description': title,
        'tags': 'hackernews',
        'replace':'no'
    }
    r = requests.get('https://api.pinboard.in/v1/posts/add', params=payload)
    #print r.url
    return 1 if isAdded(r.text) else 0

def isAdded(addresult):
    res = xml.fromstring(addresult)
    code = res.attrib["code"]
    return code == 'done'

def main():
    count = 0
    links = getSavedStories( loginToHackerNews(sys.argv[1],sys.argv[2] ),sys.argv[1] )
    for key, value in links.iteritems():
        count+=postToPinboard(sys.argv[3], key, value)

    print "Added %d links to Pinboard" % count

if __name__ == "__main__":
    main()