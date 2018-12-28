import enum
import requests
from bs4 import BeautifulSoup


MIN_SENATE = 80
MAX_SENATE = 115
MIN_HOUSE = 102
MAX_HOUSE = 115
MIN_CONGRESS = max(MIN_HOUSE, MIN_SENATE)
MAX_CONGRESS = min(MAX_HOUSE, MAX_SENATE)
CONGRESS_API_ENDPOINT = 'https://api.propublica.org/congress/v1/{0}/{1}.json'
CONGRESS_MEMBERS_URL = 'https://congress.gov/members'


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


class Congress(API):
    def __init__(self):
        super().__init__('congress')

    def get_senate_members(self, current=False):
        if current:
            return get_members(self, Chamber.SENATE, MAX_SENATE)
        return all_members(self, Chamber.SENATE)

    def get_house_members(self, current=False):
        if current:
            return get_members(self, Chamber.HOUSE, MAX_HOUSE)
        return all_members(self, Chamber.HOUSE)

    def get_current_members(self):
        return self.get_senate_members(True) + self.get_house_members(True)

    def get_all_members(self):
        return self.get_senate_members() + self.get_house_members()

    def get_recent_statements(self):
        return None


class Chamber(enum.Enum):
    SENATE = 'senate'
    HOUSE = 'house'


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


def send_request(self, endpoint):
    headers = {k: v for k, v in self.keys.items()}
    response = requests.get(endpoint, headers=headers)
    json = response.json()
    return json


def get_members(self, chamber, congress):
    if chamber == Chamber.SENATE:
        members_location = str(congress) + '/' + Chamber.SENATE.value
        endpoint = CONGRESS_API_ENDPOINT.format(members_location, 'members')
    elif chamber == Chamber.HOUSE:
        members_location = str(congress) + '/' + Chamber.HOUSE.value
        endpoint = CONGRESS_API_ENDPOINT.format(members_location, 'members')

    json = send_request(self, endpoint)
    members = json['results'][0]['members']

    for member in members:
        member['chamber'] = chamber.value
        member['congress'] = congress
        if member['twitter_account']:
            member['tweets'] = None

    return members


def all_members(self, chamber):
    if chamber == Chamber.SENATE:
        chamber_range = range(MIN_CONGRESS, MAX_SENATE + 1)
    elif chamber == Chamber.HOUSE:
        chamber_range = range(MIN_CONGRESS, MAX_HOUSE + 1)

    members = list()
    for congress in chamber_range:
        members += get_members(self, chamber, congress)

    return members
