"""A module for querying Bioguide data provided by the US GPO"""
import re
import requests
from bs4 import BeautifulSoup

from .const import Bioguide as bg


class BioguideQuery:
    """Object for sending HTTP POST requests to bioguide.congress.gov

    Parameters
    ----------
    **kwargs

    Arguments
    ---------
    lastname : str, optional
        The last name of a US Congress member

    firstname : str, optional
        The first name of a US Congress member

    position : {'Representative', 'Senator', 'Delegate', 'Vice President','President', \
        'Residential Commisioner', 'ContCong', 'Speaker of the House'}, optional
        The position of US Congress members.

    state : str, optional
        The two-letter abbreviation of a US State

    party : {\
        'Adams', 'Adams-Clay Republican', 'Adams-Clay Federalist', 'Adams Democrat', \
        'American Laborite', 'American Party', 'Anti-Administration', 'Anti-Jacksonian', \
        'Anti-Lecompton Democrat', 'Anti-Masonic', 'Anti-Monopolist', \
        'Conservative', 'Conservative Republican', 'Constitutional Unionist', \
        'Crawford Republicans', \
        'Democrat', 'Democrat Farmer Labor', 'Democratic Republican', \
        'Farmer Laborite', 'Federalist', 'Free Silver', 'Free Soil', \
        'Greenbacker', \
        'Independence Party (Minnesota)', 'Independent', 'Independent Democrat', \
        'Independent Republican', 'Independent Whig', \
        'Jackson Democrat', 'Jackson Federalist', 'Jackson Republican', \
        'Jacksonian', 'Jeffersonian Democrat', \
        'Labor', 'Law and Order', 'Liberal', 'Liberal Republican', \
        'National', 'National Republican', 'Nonpartisan', 'Nullifier', \
        'Opposition Party', \
        'Populist', 'Pro-Administration', 'Progressive', 'Progressive Republican', \
        'Prohibitionist', \
        'Readjuster', 'Republican', \
        'Silver Republican', 'Socialist', 'States Rights', \
        'Unconditional Unionist', 'Union Democrat', 'Union Labor', 'Union Republican', 'Unionist', \
        'Whig'}, optional
        The chosen party of a US Congress member

    congress : int or str
        Any year after 1785 OR any number starting from 0.
        Zero returns ContCong members and congress-members-turned-president.
    """

    def __init__(self, **kwargs):
        self.lastname = kwargs.get('lastname')
        self.firstname = kwargs.get('firstname')
        self.position = kwargs.get('position')
        self.state = kwargs.get('state')
        self.party = kwargs.get('party')
        self.congress = kwargs.get('congress')

    def send(self):
        """Sends an HTTP POST request to bioguide.congress.gov

        Returns
        -------
        str
            HTML response text
        """
        response = requests.post(bg.BIOGUIDE_URL_STR, self.params)
        return response.text

    @property
    def params(self):
        """Bioguide query parameters stored as a dict"""
        return {
            'lastname': self.lastname,
            'firstname': self.firstname,
            'position': self.position,
            'state': self.state,
            'party': self.party,
            'congress': self.congress
        }


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
        super().__init__()
        self[bg.RawColumns.ID] = row[0]
        self[bg.RawColumns.NAME] = row[1]
        self[bg.RawColumns.BIRTH_DEATH] = row[2]
        self[bg.RawColumns.POSTION] = row[3]
        self[bg.RawColumns.PARTY] = row[4]
        self[bg.RawColumns.STATE] = row[5]
        self[bg.RawColumns.CONGRESS] = row[6]

    @property
    def is_secondary(self):
        """Checks the presence of values to determine if a record is secondary
        Exists to help resolve cases where a member holds multiple positions
        (e.g. "Representative" and "Speaker of the House")
        """
        no_name = not self.member_name
        no_birth_year = not self.birth_death
        has_other_other_values = self.position or self.party or self.state or self.congress_year
        return no_name and no_birth_year and has_other_other_values

    @property
    def bioguide_id(self):
        """a US Congress member's Bioguide ID"""
        return self[bg.RawColumns.ID]

    @property
    def member_name(self):
        """a US Congress member's name"""
        return self[bg.RawColumns.NAME]

    @property
    def birth_death(self):
        """the lifespan of a US Congress member"""
        return self[bg.RawColumns.BIRTH_DEATH]

    @property
    def position(self):
        """the position of a US Congresss member"""
        return self[bg.RawColumns.POSTION]

    @property
    def party(self):
        """the party of a US Congress member"""
        return self[bg.RawColumns.PARTY]

    @property
    def state(self):
        """the represented state of a US Congress member"""
        return self[bg.RawColumns.STATE]

    @property
    def congress_year(self):
        """the term of a US Congress member"""
        return self[bg.RawColumns.CONGRESS]


class BioguideRawResponse:
    """Stores data from a Bioguide query as an array of BioguideRecords.
    Data is parsed from HTML using BeautifulSoup4.

    Parameters
    ----------
    response_text : str
        HTML POST reponse text from bioguide.congress.gov
    """

    def __init__(self, response_text):
        soup = BeautifulSoup(response_text, features='html.parser')
        tables = soup.findAll('table')
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
                    bg.Regex.BIOGUIDE_ID, member_link['href'])
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
        for index, record in enumerate(self.data):
            clean_record = None
            if record.is_secondary:
                last_record = self.data[index - 1]
                clean_record = {
                    bg.CleanColumns.ID: last_record['bioguide_id'],
                    bg.CleanColumns.FIRST_NAME: last_record['first_name'],
                    bg.CleanColumns.MIDDLE_NAME: last_record['middle_name'],
                    bg.CleanColumns.LAST_NAME: last_record['last_name'],
                    bg.CleanColumns.NICKNAME: last_record['nickname'],
                    bg.CleanColumns.SUFFIX: last_record['suffix'],
                    bg.CleanColumns.BIRTH_YEAR: last_record['birth_year'],
                    bg.CleanColumns.DEATH_YEAR: last_record['death_year'],
                }
            else:
                clean_record = {}
                clean_record[bg.CleanColumns.ID] = record.bioguide_id

                # parse details from bioguide fields
                name_match = re.search(bg.Regex.NAME, record.member_name)
                if name_match:
                    clean_record[bg.CleanColumns.LAST_NAME] = \
                        fix_last_name_casing(name_match.group('last'))
                    clean_record[bg.CleanColumns.FIRST_NAME] = \
                        name_match.group('first')
                else:
                    clean_record[bg.CleanColumns.LAST_NAME] = None
                    clean_record[bg.CleanColumns.FIRST_NAME] = None

                if name_match.group('middle'):
                    clean_record[bg.CleanColumns.MIDDLE_NAME] = \
                        name_match.group('middle')
                else:
                    clean_record[bg.CleanColumns.MIDDLE_NAME] = None

                nickname_match = re.search(
                    bg.Regex.NAME_NICKNAME, record.member_name)
                if nickname_match:
                    clean_record[bg.CleanColumns.NICKNAME] = \
                        nickname_match.group('nickname')
                else:
                    clean_record[bg.CleanColumns.NICKNAME] = None

                suffix_match = re.search(
                    bg.Regex.NAME_SUFFIX, record.member_name)
                if suffix_match:
                    clean_record[bg.CleanColumns.SUFFIX] = \
                        suffix_match.group('suffix')
                else:
                    clean_record[bg.CleanColumns.SUFFIX] = None

                life_years_match = \
                    re.search(bg.Regex.LIFESPAN, record.birth_death)

                clean_record[bg.CleanColumns.BIRTH_YEAR] = \
                    life_years_match.group('birth')

                clean_record[bg.CleanColumns.DEATH_YEAR] = \
                    life_years_match.group('death')

            term_match = re.search(bg.Regex.TERM, record.congress_year)

            clean_record[bg.CleanColumns.POSTION] = record.position
            clean_record[bg.CleanColumns.PARTY] = record.party
            clean_record[bg.CleanColumns.STATE] = record.state
            clean_record[bg.CleanColumns.CONGRESS] = \
                term_match.group('congress')

            clean_record[bg.CleanColumns.TERM_START] = \
                term_match.group('term_start')

            clean_record[bg.CleanColumns.TERM_END] = \
                term_match.group('term_end')

            self.data[index] = clean_record


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
        The number or year to query.
    """
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying pos corrects this
        query = BioguideQuery(congress=0, pos='ContCong')

    response = query.send()
    return BioguideCleanResponse(response).data


def get_raw_bioguide(congress_num=1):
    """Get a single Bioguide.

    Parameters
    ----------
    congress_num : int, optional
        The number or year to query.
    """
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        query = BioguideQuery(congress=0, pos='ContCong')

    response = query.send()
    return BioguideRawResponse(response).data


def congress_iter(start=1, end=None, bioguide_func=get_bioguide):
    """A generator for looping over Congresses by number or year.

    Parameters
    ----------
    start : int, optional
        The Congress number or year to begin the iterating from.
    end : int, optional
        The Congress number or year to stop iterating at.
        If None, iterating will stop at the current year.
    bioguide_func : function, optional
        The function to execute on each iteration.
    """
    if end - start > 500:
        raise bg.InvalidRangeError()

    # If start is a valid year
    if start > 1785:  # Bioguide begins at 1786
        import datetime

        if not end:
            end = datetime.datetime.now().year

        if start == 1788:  # 1788 returns Congress 1 (1789-1790)
            start = 1789  # the year of the first congress
        elif not start % 2:  # if even
            start -= 1  # make odd, because Congress 1 started on an odd year

        # skip every other year, as congressional terms are for 2 years
        # if end is odd, offset by 1 (1951 -> 1952, 1952 -> 1952)
        for i in range(start, end + (end % 2), 2):
            yield bioguide_func(i)
    else:
        if end:
            for i in range(start, end + 1):
                congress = bioguide_func(i)
                if not congress:
                    break
                yield congress
        else:
            # loop until an empty result is returned
            while True:
                congress = bioguide_func(start)
                if not congress:
                    break
                yield congress
                start += 1


def get_loader_func(start=1, end=None, load_range=False, load_raw=False):
    """Returns a function for loading bioguide data, based on the parameters given

    Parameters
    ----------
    start : int, optional
        The Congress number or year to begin the load from.
    end : int, optional
        The Congress number or year to end the load at.
        If None, the loading will stop at the current year.
    load_range : bool, optional
        Specifies whether to load one congress, or load all congresses to present date.
        Only used if end is None.
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

    def load_bioguide():
        return func(start)
    return load_bioguide
