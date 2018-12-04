import tweepy
import json

consumer_api_key = '2cxr421lek7AuoJZB1zMVkLDr'
consumer_api_secret = 'V2HwjXymsmFcpHeC6Hfb90acpeKG0NXWDLr0uCBqTpPRnSG38p'
access_token = '2349631081-8KYghawl484QLfeMRXRodwSyo9BVqcO24RGuK4z'
access_token_secret = 'yZcbqQOOvmGWo3sd2F69LjGFFTjc5NrgIlXpVrthvNBqR'

fd = open('test.json', 'w')

class TestListener(tweepy.StreamListener):
	def on_status(self, status):
		json_data = status._json
		text = json_data['text']
		is_retweeted = 'retweeted_status' in json_data
		if is_retweeted:
			if json_data['retweeted_status']['truncated']:
				# there is an extended tweet
				text = json_data['retweeted_status']['extended_tweet']['full_text']
			else:
				text = json_data['retweeted_status']['text']
		else:
			if json_data['truncated']:
				# there is an extended tweet
				text = json_data['extended_tweet']['full_text']
			else:
				text = json_data['text']
		created_at = json_data['created_at']
		fd.write(text.replace("\n", ' '))# json.dump(text, fd)
		fd.write('\n')
		# fd.write("\n")

auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
streamListener = TestListener()
stream = tweepy.Stream(auth = api.auth, listener = streamListener, tweet_mode='extended')
stream.filter(track=['Trump'], languages=['en'])