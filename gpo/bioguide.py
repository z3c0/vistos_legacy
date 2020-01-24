"""A module for querying Bioguide data provided by the US GPO"""
import re
from typing import List, Callable, Iterable, Any, Dict, Optional, Union

import requests
from bs4 import BeautifulSoup, Tag, NavigableString

from .const import Bioguide as bg


class BioguideQuery:
    """Object for sending HTTP POST requests to bioguide.congress.gov/biosearch

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

    def send(self) -> str:
        """Sends an HTTP POST request to bioguide.congress.gov, returning the resulting HTML text"""
        response = requests.post(bg.BIOGUIDE_URL_STR, self.params)
        return response.text

    @property
    def params(self) -> dict:
        """Returns query parameters as a dictionary"""
        return vars(self)


class BioguideExtrasQuery:
    """Object for sending HTTP GET requests for extra content available from the Bioguide"""

    def __init__(self, extra_type: bg.Extras, bioguide_id: str):
        self._index = bioguide_id
        self._url = extra_type.value

    def send(self) -> str:
        """Sends an HTTP GET request to bioguide.congress.gov/scripts/biodisplay.pl,
        returning the resulting HTML text
        """
        response = requests.get(self._url, self.params)
        return response.text

    @property
    def params(self) -> Dict[str, str]:
        """Returns query parameters as a dictionary"""
        return {'index': self._index}


class BioguideRawRecord(dict):
    """Maps record from the Bioguide to a dict-like object.
    BioguideRawRecord lists can be passed to pandas.DataFrame
    """

    def __init__(self, row: List[Optional[str]]):
        super().__init__()
        self[bg.RawColumns.ID] = row[0]
        self[bg.RawColumns.NAME] = row[1]
        self[bg.RawColumns.BIRTH_DEATH] = row[2]
        self[bg.RawColumns.POSTION] = row[3]
        self[bg.RawColumns.PARTY] = row[4]
        self[bg.RawColumns.STATE] = row[5]
        self[bg.RawColumns.CONGRESS] = row[6]

    @property
    def is_secondary(self) -> bool:
        """Checks the presence of values to determine if a record is secondary.
        Exists to help resolve cases where a member holds multiple positions
        (e.g. "Representative" and "Speaker of the House").
        """
        no_name = not self.member_name
        no_birth_year = not self.birth_death
        has_other_values = bool(
            self.position or self.party or self.state or self.congress_year)
        return no_name and no_birth_year and has_other_values

    @property
    def bioguide_id(self) -> str:
        """a US Congress member's Bioguide ID"""
        return self[bg.RawColumns.ID]

    @property
    def member_name(self) -> str:
        """a US Congress member's name"""
        return self[bg.RawColumns.NAME]

    @property
    def birth_death(self) -> str:
        """the lifespan of a US Congress member"""
        return self[bg.RawColumns.BIRTH_DEATH]

    @property
    def position(self) -> str:
        """the position of a US Congresss member"""
        return self[bg.RawColumns.POSTION]

    @property
    def party(self) -> str:
        """the party of a US Congress member"""
        return self[bg.RawColumns.PARTY]

    @property
    def state(self) -> str:
        """the represented state of a US Congress member"""
        return self[bg.RawColumns.STATE]

    @property
    def congress_year(self) -> str:
        """the term of a US Congress member"""
        return self[bg.RawColumns.CONGRESS]


class BioguideCleanRecord(dict):
    """Maps cleaned record from the Bioguide to a dict-like object.
    BioguideCleanRecord lists can be passed to pandas.DataFrame

    Arguments
    ---------
    see five.gpo.const.Bioguide.CleanColumns
    """

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            self[key] = value

    @property
    def bioguide_id(self) -> str:
        """a US Congress member's Bioguide ID"""
        return self[bg.CleanColumns.ID]

    @property
    def first_name(self) -> str:
        """a US Congress member's first name"""
        return self[bg.CleanColumns.FIRST_NAME]

    @property
    def middle_name(self) -> str:
        """a US Congress member's middle name"""
        return self[bg.CleanColumns.MIDDLE_NAME]

    @property
    def last_name(self) -> str:
        """a US Congress member's surname"""
        return self[bg.CleanColumns.LAST_NAME]

    @property
    def nickname(self) -> str:
        """a US Congress member's prefered name"""
        return self[bg.CleanColumns.NICKNAME]

    @property
    def suffix(self) -> str:
        """a US Congress member's name suffix"""
        return self[bg.CleanColumns.SUFFIX]

    @property
    def birth_year(self) -> str:
        """a US Congress member's year of birth"""
        return self[bg.CleanColumns.BIRTH_YEAR]

    @property
    def death_year(self) -> str:
        """a US Congress member's year of death"""
        return self[bg.CleanColumns.DEATH_YEAR]

    @property
    def position(self) -> str:
        """a US Congress member's position"""
        return self[bg.CleanColumns.POSITION]

    @property
    def party(self) -> str:
        """a US Congress member's party"""
        return self[bg.CleanColumns.PARTY]

    @property
    def state(self) -> str:
        """a US Congress member's represented state"""
        return self[bg.CleanColumns.STATE]

    @property
    def congress(self) -> str:
        """The congress number of a US Congress member's term"""
        return self[bg.CleanColumns.CONGRESS]

    @property
    def term_start(self) -> str:
        """The beginning year of a US Congress member's term"""
        return self[bg.CleanColumns.TERM_START]

    @property
    def term_end(self) -> str:
        """The ending year of a US Congress member's term"""
        return self[bg.CleanColumns.TERM_END]


class BiographyRecord(dict):
    """Maps Bioguide biography data to a dict-like object.
    Similar to a BioguideRawRecord, lists of BiographyRecords can be parsed by pandas.DataFrame
    """

    def __init__(self, bioguide_id: str, biography: str):
        super().__init__()
        self[bg.BiographyColumns.ID] = bioguide_id
        self[bg.BiographyColumns.BIOGRAPHY] = biography

    @property
    def biography(self) -> str:
        """The biography of a US Congress Member"""
        return self[bg.BiographyColumns.BIOGRAPHY]


class ResourceRecord(dict):
    """Maps Bioguide resource data to a dict-like object.
    Similar to a BioguideRawRecord, lists of ResourceRecords can be parsed by pandas.DataFrame
    """

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            self[key] = value

    @property
    def primary_institution(self) -> str:
        """The institution that a resource is attributed too"""
        return self[bg.ResourceColumns.PRIM_INSTITUTION]

    @property
    def secondary_institution(self) -> str:
        """The child institution that a resource is attributed too"""
        return self[bg.ResourceColumns.SEC_INSTITUTION]

    @property
    def location(self) -> str:
        """The city of the attributed institution"""
        return self[bg.ResourceColumns.LOCATION]

    @property
    def category(self) -> str:
        """The medium of the resource"""
        return self[bg.ResourceColumns.CATEGORY]

    @property
    def summary(self) -> str:
        """The summary of the resource"""
        return self[bg.ResourceColumns.SUMMARY]

    @property
    def details(self) -> str:
        """The detailed explanation of the resource"""
        return self[bg.ResourceColumns.DETAILS]


class BibliographyRecord(dict):
    """Maps Bioguide bibliography data to a dict-like object.
    Similar to a BioguideRawRecord, lists of BibliographyRecords can be parsed by pandas.DataFrame
    """

    def __init__(self, bioguide_id, biography):
        super().__init__()
        self[bg.BiographyColumns.ID] = bioguide_id
        self[bg.BiographyColumns.BIOGRAPHY] = biography

    @property
    def bioguide_id(self):
        """A US Congress Member's Bioguide ID"""
        return self[bg.BibliographyColumns.ID]

    @property
    def citation(self):
        """A citation from the bibliography of a US Congress Member"""
        return self[bg.BibliographyColumns.CITATION]


def _parse_raw_records(response_text: str) -> List[BioguideRawRecord]:
    """Stores data from a Bioguide query as a list of BioguideRawRecords"""
    soup = BeautifulSoup(response_text, features='html.parser')
    tables = soup.findAll('table')

    try:
        results_table = tables[1]  # the first table is a header
        results_rows = results_table.findAll('tr')
    except IndexError:
        results_rows = []

    data = []

    for table_row in results_rows[1:]:
        td_array = table_row.findAll('td')
        member_link = td_array[0].find('a')
        if member_link:
            id_match = re.search(
                bg.Regex.BIOGUIDE_ID, member_link['href'])
            bioguide_id = id_match.group('bioguide_id')
        else:
            bioguide_id = None

        row = [bioguide_id] + [td.text.strip() for td in td_array]
        data.append(BioguideRawRecord(row))

    return data


def _parse_clean_records(response_text) -> List[BioguideCleanRecord]:
    """Uses re to parse sub-details from the default fields provided by the Bioguide.

    Parameters
    ----------
    response_text : str
        HTML POST reponse text from bioguide.congress.gov

    Returns
    -------
    list of BioguideCleanRecord
        Bioguide data processed into more granular fields
    """

    data = _parse_raw_records(response_text)

    clean_data = []
    for index, record in enumerate(data):
        clean_record = None
        if record.is_secondary:
            last_record = clean_data[index - 1]
            clean_record = {
                bg.CleanColumns.ID: last_record.bioguide_id,
                bg.CleanColumns.FIRST_NAME: last_record.first_name,
                bg.CleanColumns.MIDDLE_NAME: last_record.middle_name,
                bg.CleanColumns.LAST_NAME: last_record.last_name,
                bg.CleanColumns.NICKNAME: last_record.nickname,
                bg.CleanColumns.SUFFIX: last_record.suffix,
                bg.CleanColumns.BIRTH_YEAR: last_record.birth_year,
                bg.CleanColumns.DEATH_YEAR: last_record.death_year,
            }
        else:
            clean_record = {}
            clean_record[bg.CleanColumns.ID] = record.bioguide_id

            # parse details from bioguide fields
            name_match = re.search(bg.Regex.NAME, record.member_name)
            if name_match:
                clean_record[bg.CleanColumns.LAST_NAME] = \
                    _fix_last_name_casing(name_match.group('last'))
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

        clean_record[bg.CleanColumns.POSITION] = record.position
        clean_record[bg.CleanColumns.PARTY] = record.party
        clean_record[bg.CleanColumns.STATE] = record.state
        clean_record[bg.CleanColumns.CONGRESS] = \
            term_match.group('congress')

        clean_record[bg.CleanColumns.TERM_START] = \
            term_match.group('term_start')

        clean_record[bg.CleanColumns.TERM_END] = \
            term_match.group('term_end')

        clean_data.append(BioguideCleanRecord(**clean_record))

    return clean_data


def _parse_biography(bioguide_id: str, response_text: str) -> BiographyRecord:
    """Processes data from a Biography query.
    Data is parsed from HTML using BeautifulSoup4

    Parameters
    ----------
    bioguide_id : str
        The bioguide ID of the congress member queried. This must be provided \
        because a bioguide ID is not included in the biography results.

    response_text : str
        HTML GET response text from bioguide.congress.gov/scripts/biodisplay.pl

    Returns
    -------
    BiographyRecord
        The biography of the given Congress member
    """
    # TODO: parse bioguide_id from navigation bar of biography page
    soup = BeautifulSoup(response_text, features='html.parser')
    bio = soup.find_all('p')[0].text

    return BiographyRecord(bioguide_id, str(bio).strip())


def _parse_resources(bioguide_id: str, response_text: str) -> List[ResourceRecord]:
    """Processes data from a Resources query.
    The structure of Resources data is denoted by blank <br> tags and styling tags, like <b> or <i>

    Data is parsed from HTML using BeautifulSoup4

    Parameters
    ----------
    bioguide_id : str
        The bioguide ID of the congress member queried. This must be provided \
        because a bioguide ID is not included in the resource results.

    response_text : str
        HTML GET response text from bioguide.congress.gov/scripts/guidedisplay.pl

    Returns
    -------
    list of ResourceRecord
        A list of resources for a given Congress member
    """
    # pylint:disable=too-many-locals,too-many-branches
    # TODO: parse bioguide_id from navigation bar of resources page
    # TODO: Make lintable
    data = []

    soup = BeautifulSoup(response_text, features='html.parser')
    # TODO: replace with more precise select
    section_headers = soup.find_all('b')
    for header in section_headers:
        section_header = [header.text]
        current_element = header
        while True:
            if _is_i_tag(current_element):
                break

            if isinstance(current_element, NavigableString):
                text = current_element.replace('\r', '').replace('\n', '')
                if text != '':
                    section_header.append(text)

            current_element = current_element.next_sibling

        resource_categories = []
        while current_element:
            if _is_b_tag(current_element):
                break

            if _is_i_tag(current_element):
                resource_categories.append(current_element)

            current_element = current_element.next_sibling

        del current_element

        primary_insitution = section_header[0]
        secondary_institution = section_header[1]
        location = section_header[2]

        del section_header

        for category_element in resource_categories:
            resource_element = category_element.next_sibling
            resource_content = []
            while resource_element:
                if _is_i_tag(resource_element) or _is_b_tag(resource_element):
                    break

                if isinstance(resource_element, NavigableString):
                    text = resource_element.replace(
                        '\r', '').replace('\n', '')
                    if text != '':
                        resource_content.append(text.strip())

                resource_element = resource_element.next_sibling

            category = category_element.text.replace(':', '').strip()
            summary = resource_content[0]
            details = resource_content[1]

            record = ResourceRecord(
                bioguide_id=bioguide_id,
                primary_institution=primary_insitution,
                secondary_institution=secondary_institution,
                location=location,
                category=category,
                summary=summary,
                details=details)

            data.append(record)

    return data
    # pylint:enable=too-many-locals,too-many-branches


def _parse_bibliography(bioguide_id: str, response_text: str) -> List[BibliographyRecord]:
    """Stores data from a Bibliography query

    Data is parsed from HTML using BeautifulSoup4
    """
    # TODO: parse bioguide_id from navigation bar of bibliography page
    soup = BeautifulSoup(response_text, features='html.parser')
    all_works = soup.find('all-works')
    data = []

    current_record = str()
    line_breaks_encountered = 0
    for element in all_works:
        if isinstance(element, Tag) and element.name == 'br' and not line_breaks_encountered:
            data.append(BibliographyRecord(
                bioguide_id, current_record))
            line_breaks_encountered += 1
            continue

        if isinstance(element, Tag) and element.name == 'br' and line_breaks_encountered == 1:
            current_record = str()
            line_breaks_encountered = 0
            continue

        if _is_i_tag(element):
            current_record += ' \'' + element.text + '\''
        else:
            current_record += element.replace('\r',
                                              '').replace('\n', '').strip()

    return data


def _get_bioguide(congress_num=1) -> List[BioguideCleanRecord]:
    """Get a single Bioguide and clean the response"""
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying pos corrects this
        query = BioguideQuery(congress=0, pos='ContCong')

    response = query.send()
    clean_records = _parse_clean_records(response)
    return clean_records


def _get_raw_bioguide(congress_num=1) -> List[BioguideRawRecord]:
    """Get a single Bioguide"""
    if congress_num:
        query = BioguideQuery(congress=congress_num)
    else:
        query = BioguideQuery(congress=0, pos='ContCong')

    response = query.send()
    raw_records = _parse_raw_records(response)
    return raw_records


def _congress_iter(start=1, end=None, bioguide_func=_get_bioguide) -> Iterable[int]:
    """A generator for looping over Congresses by number or year.
    Ranges that occur after 1785 are handled as years.
    """
    if bg.FIRST_VALID_YEAR > start and end > bg.FIRST_VALID_YEAR:
        raise bg.InvalidRangeError()

    # If start is a valid year
    if start > bg.FIRST_VALID_YEAR:  # Bioguide begins at 1786
        import datetime

        if not end:
            end = datetime.datetime.now().year

        # offset values to fit range()
        if start == 1788:  # 1788 returns Congress 1 (1789-1790)
            start = 1789  # the year of the first congress
        elif not start % 2:  # if even
            start -= 1  # make odd, because Congress 1 started on an odd year

        # if end is odd, offset by 1 (1951 -> 1952, 1952 -> 1952)
        end = end + (end % 2)

        # skip every other year, as congressional terms are for 2 years
        for i in range(start, end, 2):
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


def _is_b_tag(element: Any) -> bool:
    return isinstance(element, Tag) and element.name == 'b'


def _is_i_tag(element: Any) -> bool:
    return isinstance(element, Tag) and element.name == 'i'


def _fix_last_name_casing(name: str) -> str:
    """Converts uppercase text to capitalized"""
    # Addresses name prefixes, like "Mc-" or "La-"
    if re.match(r'^[A-Z][a-z][A-Z]', name):
        start_pos = 3
    else:
        start_pos = 1

    capital_case = name[:start_pos] + name[start_pos:].lower()
    return capital_case


def get_resources(bioguide_id: str) -> List[ResourceRecord]:
    """Get a single Bioguide resource list"""
    query = BioguideExtrasQuery(bg.Extras.RESOURCES, bioguide_id)
    response = query.send()

    return _parse_resources(bioguide_id, response)


def get_biography(bioguide_id: str) -> BiographyRecord:
    """Get a single Bioguide biography

    Parameters
    ----------
    bioguide_id : str
        The bioguide ID of a Congress Member

    Returns
    -------
    BiographyRecord
        Given Congress Member's biography
    """
    query = BioguideExtrasQuery(bg.Extras.BIOGRAPHY, bioguide_id)
    response = query.send()

    return _parse_biography(bioguide_id, response)


def get_bibliography(bioguide_id: str) -> List[BibliographyRecord]:
    """Get a single Bioguide bibliography

    Parameters
    ----------
    bioguide_id : str
        The bioguide ID of a Congress Member

    Returns
    -------
    list of str
        A list of bibliography citations, formatted in Chicago/Turabian style
    """
    query = BioguideExtrasQuery(bg.Extras.BIBLIOGRAPHY, bioguide_id)
    response = query.send()

    return _parse_bibliography(bioguide_id, response)


def get_member_bioguide(first_name: str, last_name: str):
    """Get the bioguide information for a single member

    Parameters
    ----------
    first_name : str
        The first name of the member to be queried
    last_name : str
        The last name of the member to be queried
    """
    query = BioguideQuery(firstname=first_name, lastname=last_name)
    response = query.send()

    return _parse_clean_records(response)


def get_bioguide_func(start=1, end=None, load_range=False, load_raw=False) -> \
        Callable[[], Union[List[BioguideRawRecord], List[BioguideCleanRecord]]]:
    """Returns a function for loading bioguide data, based on the parameters given"""
    if load_raw:
        func = _get_raw_bioguide
    else:
        func = _get_bioguide

    if load_range:
        def load_multiple_bioguides():
            bioguides = []
            for bioguide in _congress_iter(start, end, func):
                bioguides += bioguide

            return bioguides

        return load_multiple_bioguides

    def load_bioguide():
        return func(start)
    return load_bioguide
