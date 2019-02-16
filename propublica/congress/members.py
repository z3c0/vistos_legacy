import enum
import requests
from five.tools.api import API, send_request


MIN_SENATE = 80
MAX_SENATE = 115
MIN_HOUSE = 102
MAX_HOUSE = 115
MIN_CONGRESS = max(MIN_HOUSE, MIN_SENATE)
MAX_CONGRESS = min(MAX_HOUSE, MAX_SENATE)
CONGRESS_API_ENDPOINT = 'https://api.propublica.org/congress/v1/{0}/{1}.json'
CONGRESS_MEMBERS_URL = 'https://congress.gov/members'


class CongressMembers(API):
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


def get_members(self, chamber, congress):
    if chamber == Chamber.SENATE:
        members_location = str(congress) + '/' + Chamber.SENATE.value
        endpoint = CONGRESS_API_ENDPOINT.format(members_location, 'members')
    elif chamber == Chamber.HOUSE:
        members_location = str(congress) + '/' + Chamber.HOUSE.value
        endpoint = CONGRESS_API_ENDPOINT.format(members_location, 'members')

    json = send_request(self, endpoint)
    if json is None:
        return

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
        m = get_members(self, chamber, congress)
        if m is not None:
            members += m

    return members
