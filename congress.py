from requests import get
from enum import Enum
from . import util

MIN_SENATE = 80
MAX_SENATE = 115
MIN_HOUSE = 102
MAX_HOUSE = 115
API_ENDPOINT = 'https://api.propublica.org/congress/v1/{0}/{1}'


def send_request(self, endpoint):
	headers = {self.header: self.key}
	response = get(endpoint, headers=headers)
	json = response.json()
	return json


def get_members(self, chamber, congress):
	if chamber == Chamber.SENATE:
		members_endpoint = str(congress) + '/' + Chamber.SENATE.value
		endpoint = API_ENDPOINT.format(members_endpoint, 'members.json')
	elif chamber == Chamber.HOUSE:
		members_endpoint = str(congress) + '/' + Chamber.HOUSE.value
		endpoint = API_ENDPOINT.format(members_endpoint, 'members.json')

	json = send_request(self, endpoint)
	members = json['results'][0]['members']

	for member in members:
		member['chamber'] = chamber.value
		member['congress'] = congress

	return members


def all_members(self, chamber):
	if chamber == Chamber.SENATE:
		chamber_range = range(MIN_SENATE, MAX_SENATE + 1)
	elif chamber == Chamber.HOUSE:
		chamber_range = range(MIN_HOUSE, MAX_HOUSE + 1)

	members = list()
	for congress in chamber_range:
		members += get_members(self, chamber, congress)

	return members



class Congress(util.API):
	def __init__(self):
		util.refresh_api_pickle()
		api_keys = util.pickle_to_dict('api.pickle')
		super().__init__('congress', api_keys)

	def get_senate_members(self, current=False):
		if current: return get_members(self, Chamber.SENATE, MAX_SENATE)
		return all_members(self, Chamber.SENATE)

	def get_house_members(self, current=False):
		if current: return get_members(self, Chamber.HOUSE, MAX_HOUSE)
		return all_members(self, Chamber.HOUSE)

	def get_current_members(self):
		return self.get_senate_members(True) + self.get_house_members(True)

	def get_all_members(self):
		return self.get_senate_members() + self.get_house_members()

	def get_recent_statements(self):
		return None


class Chamber(Enum):
	SENATE = 'senate'
	HOUSE = 'house'