# -*- coding: utf-8 -*-

import sys,getopt,got,datetime,codecs

def main(argv):

	if len(argv) == 0:
		print 'You must pass some parameters. Use \"-h\" to help.'
		return
		
	if len(argv) == 1 and argv[0] == '-h':
		print """\nTo use this jar, you can pass the folowing attributes:
    username: Username of a specific twitter account (without @)
    target: Username of account to which tweet is directed towards (i.e. the account mentioned in the tweet)
       since: The lower bound date (yyyy-mm-aa)
       until: The upper bound date (yyyy-mm-aa)
 querysearch: A query text to be matched
   maxtweets: The maximum number of tweets to retrieve
      hateid: The ID corresponding to the dataset that the tweet belongs to (yyyymmrr) where 'r' means rank
     csvfile: The path + name for the .csv file where the tweets will be stored

 \nExamples:
 # Example 1 - Get tweets by username [barackobama]
 python Export.py --username 'barackobama' --maxtweets 1\n

 # Example 2 - Get tweets by query search [europe refugees]
 python Export.py --querysearch 'europe refugees' --maxtweets 1\n

 # Example 3 - Get tweets by username and bound dates [barackobama, '2015-09-10', '2015-09-12']
 python Export.py --username 'barackobama' --since 2015-09-10 --until 2015-09-12 --maxtweets 1\n"""
		return
 
	try:
		opts, args = getopt.getopt(argv, "", ("username=", "target=", "since=", "until=", "querysearch=", "maxtweets=", "hateid=", "csvfile="))
		
		tweetCriteria = got.manager.TweetCriteria()
		csvfile = "output_got.csv"
		hateid = "00000000"
		
		for opt,arg in opts:
			if opt == '--username':
				tweetCriteria.username = arg
			
			elif opt == '--target':
				tweetCriteria.target = arg
			
			elif opt == '--since':
				tweetCriteria.since = arg
				
			elif opt == '--until':
				tweetCriteria.until = arg
				
			elif opt == '--querysearch':
				tweetCriteria.querySearch = arg
				
			elif opt == '--maxtweets':
				tweetCriteria.maxTweets = int(arg)
		
			elif opt == '--hateid':
				hateid = arg
		
			elif opt == '--csvfile':
				csvfile = arg
		
		outputFile = codecs.open(csvfile, "w+", "utf-8")
		
		outputFile.write('username;date;retweets;favorites;text;geo;mentions;hashtags;id;permalink;hateid')
		
		print 'Searching...\n'
		
		def receiveBuffer(tweets):
			for t in tweets:
				t.hateid = hateid
				outputFile.write(('\n%s;%s;%d;%d;"%s";%s;%s;%s;"%s";%s;%s' % (t.username, t.date.strftime("%Y-%m-%d %H:%M"), t.retweets, t.favorites, t.text, t.geo, t.mentions, t.hashtags, t.id, t.permalink, t.hateid)))
			outputFile.flush();
			print 'More %d saved on file...\n' % len(tweets)
		
		got.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)
		
	except arg:
		print 'Arguments parser error, try -h' + arg
	finally:
		outputFile.close()
		print ('Done. Output file generated at %s.' % (csvfile))

if __name__ == '__main__':
	main(sys.argv[1:])
