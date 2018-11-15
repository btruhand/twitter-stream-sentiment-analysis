import tweepy
import time

consumer_api_key = '2cxr421lek7AuoJZB1zMVkLDr'
consumer_api_secret = 'V2HwjXymsmFcpHeC6Hfb90acpeKG0NXWDLr0uCBqTpPRnSG38p'
access_token = '2349631081-8KYghawl484QLfeMRXRodwSyo9BVqcO24RGuK4z'
access_token_secret = 'yZcbqQOOvmGWo3sd2F69LjGFFTjc5NrgIlXpVrthvNBqR'

class TestListener(tweepy.StreamListener):
	def on_status(self, status):
		print(status.text)

auth = tweepy.OAuthHandler(consumer_api_key, consumer_api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
streamListener = TestListener()
stream = tweepy.Stream(auth = api.auth, listener = streamListener)
stream.filter(track=['global warming'], languages=['en'], async=True)
print('ok')
time.sleep(5)
stream.filter(track=['Trump'], languages=['en'])