import tweepy
import json


class API(object):
    name = str()
    keys = dict()

    def __init__(self, api_name):
        refresh_api_pickle()
        api_key_dict = pickle_to_dict('five-api.pickle')

        self.name = api_name
        for i, api in enumerate(api_key_dict['api']):
            if api == api_name:
                self.keys[api_key_dict['header'][i]] = api_key_dict['key'][i]


def refresh_api_pickle():
    api_dict = csv_to_dict('five-api.tsv', seperator='\t')
    dict_to_pickle(api_dict, 'five-api.pickle')


def pickle_to_dict(path):
    import pickle

    with open(path, 'rb') as pickle_file:
        result = pickle.load(pickle_file)

    pickle_file.close()

    return result


def dict_to_pickle(dict_to_write, path):
    import pickle

    with open(path, 'wb') as pickle_file:
        pickle.dump(dict_to_write, pickle_file)

    pickle_file.close()


def csv_to_dict(path, seperator=','):
    result = dict()

    with open(path, 'r') as file:
        first_line = str(file.readline())
        headers = first_line.split(seperator)

        for line in file:
            values = line.split(seperator)
            for i, header in enumerate(headers):
                header = header.strip()
                value = values[i].strip()
                try:
                    result[header] += [value]
                except KeyError:
                    result[header] = [value]

    file.close()
    return result


class Twitter():
    def get_oauth_handler(self):
        api = API('twitter')
        consumer_key = api.keys['Consumer Key']
        consumer_secret = api.keys['Consumer Secret']
        access_token = api.keys['Access Token']
        access_token_secret = api.keys['Access Token Secret']

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth

    def get_tweets(self, screen_name, page_count=None):
        # TODO: increase limit beyond ~3000 tweets
        api = tweepy.API(Twitter.get_oauth_handler(self))

        def tweets(count=0):
            cursor = tweepy.Cursor(
                api.user_timeline, screen_name=screen_name, tweet_mode='extended')
            timeline = cursor.pages(count)

            for page in timeline:
                for status in page:
                    yield status.full_text

        return tweets(page_count)
