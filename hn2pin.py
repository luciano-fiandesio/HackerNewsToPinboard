#!/usr/bin/env python
"""Python-Pinboard

Python script for syncronizing Hacker News <http://news.ycombinator.com> saved stories to Pinboard <http://pinboard.in/> via its API.

Originally written on Pythonista on iPad
"""

__version__ = "1.0"
__license__ = "BSD"
__copyright__ = "Copyright 2012, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/>"

import re
import sys
import urllib
import urlparse
from bs4 import BeautifulSoup
import requests
from types import *
import xml.etree.ElementTree as xml

HACKERNEWS = 'http://news.ycombinator.com/'

def getSavedStories(cookies):
    print "get saved stories"
    savedStories = {}
    saved = requests.get('https://news.ycombinator.com/saved?id=koevet',cookies=cookies)
    #print saved.status_code
    soup = BeautifulSoup(saved.content)

    for tag in soup.findAll('td',attrs={'class':'title'}):
        if type(tag.a) is not NoneType:
            
            _href = tag.a['href']
            if not str.startswith(str(_href), '/x?fnid'): # skip the 'More' link
                _href = HACKERNEWS+_href if str.startswith(str(_href), 'item?') else _href
                savedStories[_href] = tag.a.text
            
    return savedStories

def loginToHackerNews(username, password):
    # Request a blank login page to harvest the fnid (a CSRF-type key).
    r = requests.get('https://news.ycombinator.com/newslogin')
    
    soup = BeautifulSoup(r.content)

    inputTag = soup.find(attrs={"name": "fnid"})
    fnid = inputTag['value']
    
    # Build the login POST data and make the login request.
    payload = {
        'fnid': fnid,
        'u': username,
        'p': password,
    }
    r = requests.post('https://news.ycombinator.com/y', data=payload)
    
    if 'Bad login' in str(r.content):
        raise Exception("Hacker News authentication failed!")
    
    return r.cookies

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
    links = getSavedStories( loginToHackerNews(sys.argv[1],sys.argv[2] ) )
    for key, value in links.iteritems():
        count+=postToPinboard(sys.argv[3], key, value)
        #print key + " > " + value

    print "Added %d links to Pinboard" % count

if __name__ == "__main__":
    main()