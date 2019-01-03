import tweepy
from five.tools.api import API


class TweetTimelinesHandler():
    def __init__(self, screen_name):
        super().__init__('twitter')
        self.screen_name = screen_name

    def get_tweets(self, screen_name, page_count=None):
        # TODO: increase limit beyond ~3000 tweets
        api = tweepy.API(get_oauth_handler(self))

        def tweets(count=0):
            cursor = tweepy.Cursor(
                api.user_timeline, screen_name=self.screen_name, tweet_mode='extended')
            timeline = cursor.pages(count)

            for page in timeline:
                for status in page:
                    yield status.full_text

        return tweets(page_count)


def get_oauth_handler(self):
    api = API('twitter')
    consumer_key = api.keys['Consumer Key']
    consumer_secret = api.keys['Consumer Secret']
    access_token = api.keys['Access Token']
    access_token_secret = api.keys['Access Token Secret']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return auth
