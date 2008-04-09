import simplejson

#www.jamendo.com/get2/id/track/json/?n=2000&order=rating_desc

#we could do that with a direct call to our API but still not sure how the import cache works.
trackIds = simplejson.load(open("trackids.txt"))