import urllib2

import simplejson


def getSynchronous(url):
    return simplejson.loads(urllib2.urlopen("http://www.jamendo.com/get2/"+url).read())