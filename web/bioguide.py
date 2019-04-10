import re
import requests
from bs4 import BeautifulSoup

from .const import *


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

    def send(self, clean_response=False):
        r = requests.post(ROOT, self.params)

        if clean_response:
            return BioguideCleanResponse(r.text)

        return BioguideRawResponse(r.text)


class BioguideRecord(dict):
    """
    Maps record from the Bioguide to a dict-like object. 
    BioguideRecord arrays can be passed to pandas.DataFrame.
    """
    def __init__(self, row):
        self[RecordColumns.ID] = row[0]
        self[RecordColumns.NAME] = row[1]
        self[RecordColumns.BIRTH_DEATH] = row[2] 
        self[RecordColumns.POSTION] = row[3]
        self[RecordColumns.PARTY] = row[4]
        self[RecordColumns.STATE] = row[5]
        self[RecordColumns.CONGRESS] = row[6]

    @property
    def is_secondary(self):
        no_name = not self.member_name
        no_birth_year = not self.birth_death
        has_other_other_values = self.position or self.party or self.state or self.congress_year
        return no_name and no_birth_year and has_other_other_values

    @property
    def bioguide_id(self):
        return self[RecordColumns.ID]

    @property
    def member_name(self):
        return self[RecordColumns.NAME]

    @property
    def birth_death(self):
        return self[RecordColumns.BIRTH_DEATH]

    @property
    def position(self):
        return self[RecordColumns.POSTION]

    @property
    def party(self):
        return self[RecordColumns.PARTY]

    @property
    def state(self):
        return self[RecordColumns.STATE]

    @property
    def congress_year(self):
        return self[RecordColumns.CONGRESS]


class BioguideRawResponse:
    """Uses BeautifulSoup4 to parse Bioguide data from HTML"""
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
            td_array = row.findAll('td')
            member_link = td_array[0].find('a')
            if member_link:
                id_match = re.search(Regex.BIOGUIDE_ID, member_link['href'])
                bioguide_id = id_match.group('bioguide_id')
            else:
                bioguide_id = None

            row = [bioguide_id] + [td.text.strip() for td in td_array]
            self.data.append(BioguideRecord(row))


class BioguideCleanResponse(BioguideRawResponse):
    """Uses re to parse sub-details from the default fields provided by the Bioguide"""
    def __init__(self, response_text):
        super().__init__(response_text)
        clean_data = []
        for r in self.data:
            if r.is_secondary:
                last_record = clean_data[-1]
                bioguide_id = last_record['bioguide_id']
                last_name = last_record['last_name']
                first_name = last_record['first_name']
                middle_name = last_record['middle_name']
                nickname = last_record['nickname']
                suffix = last_record['suffix']
                birth_year = last_record['birth_year']
                death_year = last_record['death_year']
            else:
                bioguide_id = r.bioguide_id

                # parse details from bioguide fields
                name_match = re.search(Regex.NAME, r.member_name)
                if name_match:
                    last_name = fix_last_name_casing(name_match.group('last'))
                    first_name = name_match.group('first')
                else:
                    last_name = None
                    first_name = None

                if name_match.group('middle'):
                    middle_name = name_match.group('middle')
                else:
                    middle_name = None

                nickname_match = re.search(Regex.NAME_NICKNAME, r.member_name)
                if nickname_match:
                    nickname = nickname_match.group('nickname')
                else:
                    nickname = None

                suffix_match = re.search(Regex.NAME_SUFFIX, r.member_name)
                if suffix_match:
                    suffix = suffix_match.group('suffix')
                else:
                    suffix = None

                life_years_match = re.search(Regex.LIFESPAN, r.birth_death)
                birth_year = life_years_match.group('birth')
                death_year = life_years_match.group('death')

            term_match = re.search(Regex.TERM, r.congress_year)

            congress = term_match.group('congress')
            term_start = term_match.group('term_start')
            term_end = term_match.group('term_end')

            clean_data.append({
                'bioguide_id': bioguide_id,
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

        self.data = clean_data


def fix_last_name_casing(name):
    if re.match(r'^[A-Z][a-z][A-Z]', name):
        start_pos = 3
    else:
        start_pos = 1

    capital_case = name[:start_pos] + name[start_pos:].lower()
    return capital_case


def get_congress(congress_num=1, clean=True):
    query = BioguideQuery(congress=congress_num)
    r = query.send(clean_response=clean)
    return r.data
