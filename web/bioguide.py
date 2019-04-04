import re
import requests
from bs4 import BeautifulSoup


BIOGUIDE_ROOT = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'

# regex101.com
RE_NAME_PATTERN = r'^(?P<last>[\w\.\'\- ]+),(?: \(.+\))? (?P<first>(?:[A-Z][a-z]+|[A-Z]\.?)(?:[\-\'][A-Z][a-z]+)?)(?: (?P<middle>(?:[A-Z]\.|[A-Z][a-z]+)(?:[ -]?[A-Z][a-z]+)?))?'
RE_NAME_SUFFIX_PATTERN = r'(?: (?P<suffix>(I{1,3}|IV|V|VI{1,3}|Jr\.|Sr\.))(?: |$))'
RE_NAME_NICKNAME_PATTERN = r'\((?P<nickname>.+)\)'
RE_LIFESPAN_PATTERN = r'(?P<birth>\d{4})?-(?P<death>\d{4})?'
RE_TERM_PATTERN = r'(?P<congress>[0-9]{1,3})(?:\((?P<term_start>[0-9]{4})-(?P<term_end>[0-9]{4})\))?'

class BioguideQuery:
    def __init__(self, lastname=None, firstname=None, pos=None, state=None, party=None, congress=None):
        self.lastname = lastname
        self.firstname = firstname
        self.position = pos
        self.state = state
        self.party = party
        self.congress = congress

    @property
    def params(self):
        return {
            'lastname': self.lastname,
            'firstname': self.firstname,
            'position': self.position,
            'state': self.state,
            'party': self.party,
            'congress': self.congress
        }

    def send(self):
        r = requests.post(BIOGUIDE_ROOT, self.params)
        return BioguideResponse(r.text)


class BioguideRecord:
    def __init__(self, td_array):
        self.member_name = td_array[0].text.strip()
        self.birth_death = td_array[1].text.strip()
        self.position = td_array[2].text.strip()
        self.party = td_array[3].text.strip()
        self.state = td_array[4].text.strip()
        self.congress_year = td_array[5].text.strip()

    @property
    def is_secondary(self):
        no_name = not self.member_name
        no_birth_year = not self.birth_death
        has_other_other_values = self.position or self.party or self.state or self.congress_year
        return no_name and no_birth_year and has_other_other_values


class BioguideResponse:
    def __init__(self, response_text):
        bs = BeautifulSoup(response_text, features='html.parser')
        tables = bs.findAll('table')
        try:
            results_table = tables[1]  # the first table is a header
            results_rows = results_table.findAll('tr')
        except IndexError:
            results_rows = []

        self.data = []
        for row in results_rows[1:]:
            items = row.findAll('td')
            r = BioguideRecord(items)

            if r.is_secondary:
                last_record = self.data[-1]
                last_name = last_record['last_name']
                first_name = last_record['first_name']
                middle_name = last_record['middle_name']
                nickname = last_record['nickname']
                suffix = last_record['suffix']
                birth_year = last_record['birth_year']
                death_year = last_record['death_year']
            else:
                name_match = re.search(RE_NAME_PATTERN, r.member_name)
                last_name = fix_last_name_casing(name_match.group('last'))
                first_name = name_match.group('first')

                nickname_match = re.search(RE_NAME_NICKNAME_PATTERN, r.member_name)
                if nickname_match:
                    nickname = nickname_match.group('nickname')
                else:
                    nickname = None

                if name_match.group('middle'):
                    middle_name = name_match.group('middle')
                else:
                    middle_name = None

                suffix_match = re.search(RE_NAME_SUFFIX_PATTERN, r.member_name)
                if suffix_match:
                    suffix = suffix_match.group('suffix')
                else:
                    suffix = None

                life_years = re.search(RE_LIFESPAN_PATTERN, r.birth_death)
                birth_year = life_years.group('birth')
                death_year = life_years.group('death')

            term_match = re.search(RE_TERM_PATTERN, r.congress_year)

            congress = term_match.group('congress')
            term_start = term_match.group('term_start')
            term_end = term_match.group('term_end')

            self.data.append({
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'nickname': nickname,
                'suffix': suffix,
                'birth_year': birth_year,
                'death_year': death_year,
                'position': r.position,
                'party': r.party,
                'state': r.state,
                'congress': congress,
                'term_start': term_start,
                'term_end': term_end
            })


def fix_last_name_casing(name):
    if re.match(r'^[A-Z][a-z][A-Z]', name):
        start_pos = 3
    else:
        start_pos = 1

    capital_case = name[:start_pos] + name[start_pos:].lower()
    return capital_case


def get_congress(congress_num=1):
    query = BioguideQuery(congress=congress_num)
    r = query.send()
    return r.data
