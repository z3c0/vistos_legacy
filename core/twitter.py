import tweepy, json
from util import API


class Twitter(API):
	auth = None

	def __init__(self):
		super().__init__('twitter')
		consumer_key = self.keys['Consumer Key']
		consumer_secret = self.keys['Consumer Secret']
		access_token = self.keys['Access Token']
		access_token_secret = self.keys['Access Token Secret']
		
		self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		self.auth.set_access_token(access_token, access_token_secret)


	def get_tweets(self, screen_name, page_count=None):
		# TODO: increase limit beyond ~3000 tweets
		api = tweepy.API(self.auth)
		
		def tweets(count):
			cursor = tweepy.Cursor(api.user_timeline, screen_name=screen_name, tweet_mode='extended')
			if count:
				timeline = cursor.pages(count)
			else: 
				timeline = cursor.pages()

			for page in timeline:
				for status in page:
					yield status.full_text

		return tweets(page_count)
