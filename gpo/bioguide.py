import re
import requests
from bs4 import BeautifulSoup

from .const import (
    BIOGUIDE_URL_STR, 
    BioguideRawColumns,
    BioguideCleanColumns,
    BioguideRegex
)

class BioguideQuery:
    """Object for sending HTTP POST requests to bioguide.congress.gov

    Parameters
    ----------
    lastname : str, optional
        The last name of a US Congress member
    
    firstname : str, optional
        The first name of a US Congress member
    
    pos : {'', 'Representative', 'Senator', 'Delegate', 'Vice President', 'President', 'Residential Commisioner', 'ContCong', 'Speaker of the House'}, optional
        The position of US Congress members. 
    
    state : str, optional
        The two-letter abbreviation of a US State
    party : {'', 'Adams', 'Adams-Clay Republican', 'Adams-Clay Federalist', 'Adams Democrat', 'American Laborite', 'American Party', 'Anti-Administration', 'Anti-Jacksonian', 'Anti-Lecompton Democrat', 'Anti-Masonic', 'Anti-Monopolist', 'Conservative', 'Conservative Republican', 'Constitutional Unionist', 'Crawford Republicans', 'Democrat', 'Democrat Farmer Labor', 'Democratic Republican', 'Farmer Laborite', 'Federalist', 'Free Silver', 'Free Soil', 'Greenbacker', 'Independence Party (Minnesota)', 'Independent', 'Independent Democrat', 'Independent Republican', 'Independent Whig', 'Jackson Democrat', 'Jackson Federalist', 'Jackson Republican', 'Jacksonian', 'Jeffersonian Democrat', 'Labor', 'Law and Order', 'Liberal', 'Liberal Republican', 'National', 'National Republican', 'Nonpartisan', 'Nullifier', 'Opposition Party', 'Populist', 'Pro-Administration', 'Progressive', 'Progressive Republican', 'Prohibitionist', 'Readjuster', 'Republican', 'Silver Republican', 'Socialist', 'States Rights', 'Unconditional Unionist', 'Union Democrat', 'Union Labor', 'Union Republican', 'Unionist', 'Whig'}, optional

    congress : int or str
        Any year after 1785 OR any number starting from 0 (zero returns ContCong members and congress-members-turned-president)
    """
    def __init__(self, lastname=None, firstname=None, pos=None, state=None, party=None, congress=None):
        self.lastname = lastname
        self.firstname = firstname
        self.position = pos
        self.state = state
        self.party = party
        self.congress = congress

    def send(self):
        """Sends an HTTP POST request to bioguide.congress.gov

        Returns
        -------
        str
            HTML response text
        """
        r = requests.post(BIOGUIDE_URL_STR, {
            'lastname': self.lastname,
            'firstname': self.firstname,
            'position': self.position,
            'state': self.state,
            'party': self.party,
            'congress': self.congress
        })
        return r.text


class BioguideRecord(dict):
    """Maps record from the Bioguide to a dict-like object. 
    BioguideRecord arrays can be passed to pandas.DataFrame.

    Parameters
    ----------
    row: list of str
        A list of Bioguide column values in the following order:
            1) Bioguide ID
            2) Name
            3) Birth/Death
            4) Position
            5) Party
            6) State
            7) Congress
    """
    def __init__(self, row):
        self[BioguideRawColumns.ID] = row[0]
        self[BioguideRawColumns.NAME] = row[1]
        self[BioguideRawColumns.BIRTH_DEATH] = row[2]
        self[BioguideRawColumns.POSTION] = row[3]
        self[BioguideRawColumns.PARTY] = row[4]
        self[BioguideRawColumns.STATE] = row[5]
        self[BioguideRawColumns.CONGRESS] = row[6]

    @property
    def is_secondary(self):
        """Checks the presence of values to determine if a record is secondary to the record before it
        Exists to help resolve cases where a member holds multiple positions (e.g. "Representative" and "Speaker of the House")
        """
        no_name = not self.member_name
        no_birth_year = not self.birth_death
        has_other_other_values = self.position or self.party or self.state or self.congress_year
        return no_name and no_birth_year and has_other_other_values

    @property
    def bioguide_id(self):
        return self[BioguideRawColumns.ID]

    @property
    def member_name(self):
        return self[BioguideRawColumns.NAME]

    @property
    def birth_death(self):
        return self[BioguideRawColumns.BIRTH_DEATH]

    @property
    def position(self):
        return self[BioguideRawColumns.POSTION]

    @property
    def party(self):
        return self[BioguideRawColumns.PARTY]

    @property
    def state(self):
        return self[BioguideRawColumns.STATE]

    @property
    def congress_year(self):
        return self[BioguideRawColumns.CONGRESS]


class BioguideRawResponse:
    """Stores data from a Bioguide query as an array of BioguideRecords.
    Data is parsed from HTML using BeautifulSoup4.
    
    Parameters
    ----------
    response_text : str
        HTML POST reponse text from bioguide.congress.gov
    """
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
                id_match = re.search(
                    BioguideRegex.BIOGUIDE_ID, member_link['href'])
                bioguide_id = id_match.group('bioguide_id')
            else:
                bioguide_id = None

            row = [bioguide_id] + [td.text.strip() for td in td_array]
            self.data.append(BioguideRecord(row))


class BioguideCleanResponse(BioguideRawResponse):
    """Uses re to parse sub-details from the default fields provided by the Bioguide.
    
    Parameters
    ----------
    response_text : str
        HTML POST reponse text from bioguide.congress.gov
    """
    def __init__(self, response_text):
        super().__init__(response_text)
        for i, r in enumerate(self.data):
            if r.is_secondary:
                last_record = self.data[i - 1]
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
                name_match = re.search(BioguideRegex.NAME, r.member_name)
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

                nickname_match = re.search(
                    BioguideRegex.NAME_NICKNAME, r.member_name)
                if nickname_match:
                    nickname = nickname_match.group('nickname')
                else:
                    nickname = None

                suffix_match = re.search(
                    BioguideRegex.NAME_SUFFIX, r.member_name)
                if suffix_match:
                    suffix = suffix_match.group('suffix')
                else:
                    suffix = None

                life_years_match = re.search(
                    BioguideRegex.LIFESPAN, r.birth_death)
                birth_year = life_years_match.group('birth')
                death_year = life_years_match.group('death')

            term_match = re.search(BioguideRegex.TERM, r.congress_year)

            congress = term_match.group('congress')
            term_start = term_match.group('term_start')
            term_end = term_match.group('term_end')

            self.data[i] = {
                BioguideCleanColumns.ID: bioguide_id,
                BioguideCleanColumns.FIRST_NAME: first_name,
                BioguideCleanColumns.MIDDLE_NAME: middle_name,
                BioguideCleanColumns.LAST_NAME: last_name,
                BioguideCleanColumns.NICKNAME: nickname,
                BioguideCleanColumns.SUFFIX: suffix,
                BioguideCleanColumns.BIRTH_YEAR: birth_year,
                BioguideCleanColumns.DEATH_YEAR: death_year,
                BioguideCleanColumns.POSTION: r.position,
                BioguideCleanColumns.PARTY: r.party,
                BioguideCleanColumns.STATE: r.state,
                BioguideCleanColumns.CONGRESS: congress,
                BioguideCleanColumns.TERM_START: term_start,
                BioguideCleanColumns.TERM_END: term_end
            }


def fix_last_name_casing(name):
    """Converts uppercase text to capitalized.
    
    Parameters
    ----------
    name : str
        Uppercase name to make capitalized.

    Returns
    -------
    str
        Capitalized name
    """
    # TODO: ONLY addresses prefixes, and not any other potential casing oddities. Fix this.
    # Addresses name prefixes, like "Mc-" or "La-"
    if re.match(r'^[A-Z][a-z][A-Z]', name):
        start_pos = 3
    else:
        start_pos = 1

    capital_case = name[:start_pos] + name[start_pos:].lower()
    return capital_case


def get_bioguide(congress_num=1):
    """Get a single Bioguide and clean the response.
    
    Parameters
    ----------
    congress_num : int, optional
        The number or year to query
    """
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying pos corrects this
        # TODO: Add an option for congress-members-turned-president
        query = BioguideQuery(congress=0, pos='ContCong')

    r = query.send()
    return BioguideCleanResponse(r).data


def get_raw_bioguide(congress_num=1):
    """Get a single Bioguide.
    
    Parameters
    ----------
    congress_num : int, optional
        The number or year to query
    """
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        query = BioguideQuery(congress=0, pos='ContCong')

    r = query.send()
    return BioguideRawResponse(r).data


def congress_iter(start=1, end=None, bioguide_func=get_bioguide):
    """A generator for looping over Congresses by number or year.
    
    Parameters
    ----------
    start : int, optional
        The Congress number or year to begin the iterating from.
    end : int, optional
        The Congress number or year to stop iterating at. If None, iterating will stop at the current year
    bioguide_func : function, optional
        The function to execute on each iteration
    """
    # TODO: Add error handling to prevent ranges like 1-1786

    # If start is a valid year
    if start > 1785: # Bioguide begins at 1786
        import datetime

        if not end:
            end = datetime.datetime.now().year

        if start == 1788:  # 1788 returns Congress 1 (1789-1790)
            start = 1789 # the year of the first congress
        elif not start % 2: # if even
            start -= 1 # make odd, because Congress 1 started on an odd year

        # skip every other year, as congressional terms are for 2 years
        # if end is odd, offset by 1 (1951 -> 1952, 1952 -> 1952)
        for i in range(start, end + (end % 2), 2):
            yield bioguide_func(i)
    else:
        if end:
            for i in range(start, end + 1):
                c = bioguide_func(i)
                if not c:
                    break
                yield c
        else:
            # loop until an empty result is returned
            while True:
                c = bioguide_func(start)
                if not c:
                    break
                yield c
                start += 1


def get_loader_func(start=1, end=None, load_range=False, load_raw=False):
    """Returns a function for loading bioguide data, based on the parameters given
    
    Parameters
    ----------
    start : int, optional
        The Congress number or year to begin the load from.
    end : int, optional
        The Congress number or year to end the load at. If None, the loading will stop at the current year
    load_range : bool, optional
        Only relevant if end is None; specifies whether to load one congress, or load all congresses to present date.
    load_raw : bool, optional
        Specify True to prevent five from cleaning Bioguide records (still returns a bioguide id.)
    """
    if load_raw:
        func = get_raw_bioguide
    else:
        func = get_bioguide

    if load_range:
        def load_multiple_bioguides():
            bioguide = []
            for bg in congress_iter(start, end, func):
                bioguide += bg

            return bioguide
        return load_multiple_bioguides
    else:
        def load_bioguide():
            return func(start)
        return load_bioguide
