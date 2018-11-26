import json
from tweepy import OAuthHandler, API
from pprint import PrettyPrinter

conf = json.load(open('../config.json'))['twitter-api']
auth = OAuthHandler(conf['consumer_api_key'], conf['consumer_api_secret'])
auth.set_access_token(conf['access_token'], conf['access_token_secret'])
api = API(auth)
pp = PrettyPrinter(indent=1)
1
limit = api.rate_limit_status()
pp.pprint(limit)
