import urllib,urllib2,json,re,datetime,sys,cookielib
from .. import models
from pyquery import PyQuery
import lxml

################################################
no_default='<NoDefault>'
def text(html_thing, value=no_default):
	
	if value is no_default:
		if not html_thing:
			return None

		text = []

		def add_text(tag, inside_href, no_tail=False):
			if tag.text and not isinstance(tag, lxml.etree._Comment):
				text.append(tag.text)
			for child in tag.getchildren():
				add_text(child, (tag.tag=='a'))
			if not no_tail and tag.tail:
				text.append(tag.tail)
			if tag.tag == 'a' and not inside_href:
				text.append(u' ')

		for tag in html_thing:
			add_text(tag, inside_href=False, no_tail=True)
		return ''.join(text).strip()

	for tag in html_thing:
		for child in tag.getchildren():
			tag.remove(child)
		tag.text = value
	return html_thing
###############################################


class TweetManager:
	
	def __init__(self):
		pass
 
	@staticmethod
	def getTweets(tweetCriteria, receiveBuffer = None, bufferLength = 100):
		refreshCursor = ''
	
		results = []
		resultsAux = []
		cookieJar = cookielib.CookieJar()

		active = True

		while active:
			json = TweetManager.getJsonReponse(tweetCriteria, refreshCursor, cookieJar)
			if len(json['items_html'].strip()) == 0:
				break

			refreshCursor = json['min_position']
			tweets = PyQuery(json['items_html'])('div.js-stream-tweet')
			
			if len(tweets) == 0:
				break
			
			for tweetHTML in tweets:
				tweetPQ = PyQuery(tweetHTML)
				tweet = models.Tweet()
				
				lang = tweetPQ("div.js-tweet-text-container p.TweetTextSize.js-tweet-text.tweet-text").attr("lang")
				if lang != 'en': continue
				
				usernameTweet = tweetPQ("span.username.js-action-profile-name b").text();
				dateSec = int(tweetPQ("small.time span.js-short-timestamp").attr("data-time"));
				id_str = str(tweetPQ.attr("data-tweet-id"));
				
				#####
				txt = text(tweetPQ("p.js-tweet-text"))
				#####
				
				#####
				tweet.retweets = 0
				tweet.favorites = 0
				tweet.lang = ''
				#####
				
				tweet.id_str = id_str
				tweet.username = usernameTweet
				tweet.text = txt
				tweet.date = dateSec 
				# Now an int, instead of formatting to date time 
				# (eventually to string in data file) #
				#tweet.date = datetime.datetime.utcfromtimestamp(dateSec)
				
				results.append(tweet)
				resultsAux.append(tweet)
				
				if receiveBuffer and len(resultsAux) >= bufferLength:
					receiveBuffer(resultsAux)
					resultsAux = []
				
				if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
					active = False
					break
					
		
		if receiveBuffer and len(resultsAux) > 0:
			receiveBuffer(resultsAux)
		
		return results
	
	@staticmethod
	def getJsonReponse(tweetCriteria, refreshCursor, cookieJar):
		url = "https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd&max_position=%s"
		
		urlGetData = ''
		if hasattr(tweetCriteria, 'username'):
			urlGetData += ' from:' + tweetCriteria.username
		
		if hasattr(tweetCriteria, 'target'):
			urlGetData += ' to:' + tweetCriteria.target
			
		if hasattr(tweetCriteria, 'since'):
			urlGetData += ' since:' + tweetCriteria.since
			
		if hasattr(tweetCriteria, 'until'):
			urlGetData += ' until:' + tweetCriteria.until
			
		if hasattr(tweetCriteria, 'querySearch'):
			urlGetData += ' ' + tweetCriteria.querySearch

		if hasattr(tweetCriteria, 'allTweets'):
			if tweetCriteria.allTweets:
				url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&max_position=%s"

		url = url % (urllib.quote(urlGetData), refreshCursor)

		headers = [
			('Host', "twitter.com"),
			('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
			('Accept', "application/json, text/javascript, */*; q=0.01"),
			('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
			('X-Requested-With', "XMLHttpRequest"),
			('Referer', url),
			('Connection', "keep-alive")
		]

		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
		opener.addheaders = headers

		try:
			response = opener.open(url)
			jsonResponse = response.read()
			
		except:
			print "Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.quote(urlGetData)
			sys.exit()
			return
		
		dataJson = json.loads(jsonResponse)

		return dataJson		
