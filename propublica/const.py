

MIN_SENATE = 80
MAX_SENATE = 116
MIN_HOUSE = 102
MAX_HOUSE = 116
MIN_CONGRESS = max(MIN_HOUSE, MIN_SENATE)
MAX_CONGRESS = min(MAX_HOUSE, MAX_SENATE)
CONGRESS_API_ENDPOINT = 'https://api.propublica.org/congress/v1/{0}/{1}.json'
CONGRESS_MEMBERS_URL = 'https://congress.gov/members'
