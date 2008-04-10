import simplejson

#http://www.jamendo.com/get2/id/track/json/track_album/?n=10000&order=rating_desc

#we could do that with a direct call to our API but still not sure how the import cache works.
trackIds = simplejson.load(open("trackids.txt"))