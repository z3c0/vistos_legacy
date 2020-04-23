"""A module for querying Bioguide data provided by the US GPO"""
import re
import json
import requests

from typing import List, Optional, Set, Callable, Iterable
from xml.etree import ElementTree as XML
from bs4 import BeautifulSoup

from .const import Bioguide as bg


class BioguideRetroQuery:
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

    def __init__(self, last_name=None, first_name=None, position=None, state=None, party=None, congress=None):
        self.last_name = last_name
        self.first_name = first_name
        self.position = position
        self.state = state
        self.party = party
        self.year_or_congress = congress
        self.verification_token = _get_verification_token()

    def send(self) -> requests.Response:
        """Sends an HTTP POST request to bioguide.congress.gov, returning the resulting HTML text"""
        response = requests.post(bg.BIOGUIDERETRO_SEARCH_URL_STR, self.params)
        return response

    def refresh_verification_token(self) -> None:
        """Fetches a new verification token"""
        self.verification_token = _get_verification_token()

    @property
    def params(self) -> dict:
        """Returns query parameters as a dictionary"""
        return {
            'LastName': self.last_name,
            'FirstName': self.first_name,
            'Position': self.position,
            'State': self.state,
            'Party': self.party,
            'YearOrCongress': self.year_or_congress,
            'submitButton': 'submit',
            '__RequestVerificationToken': self.verification_token
        }


class BioguideTermRecord(dict):
    def __init__(self, xml_data: XML.Element) -> None:
        super().__init__()
        congress_number = int(
            str(xml_data.find('congress-number').text))
        self[bg.TermFields.CONGRESS_NUMBER] = congress_number

        year_map = bg.CongressNumberYearMap()
        self[bg.TermFields.TERM_START] = year_map.get_start_year(
            congress_number)
        self[bg.TermFields.TERM_END] = year_map.get_end_year(
            congress_number)

        self[bg.TermFields.POSITION] = str(xml_data.find('term-position').text)
        self[bg.TermFields.STATE] = str(xml_data.find('term-state').text)
        self[bg.TermFields.PARTY] = str(xml_data.find('term-party').text)

    def __str__(self) -> str:
        return json.dumps(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BioguideTermRecord) \
            and self.congress_number == o.congress_number \
            and self.start_year == o.start_year \
            and self.end_year == o.end_year \
            and self.position == o.position \
            and self.state == o.state \
            and self.party == o.party

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    @property
    def congress_number(self) -> int:
        """a Congressional term's number"""
        return self[bg.TermFields.CONGRESS_NUMBER]

    @property
    def start_year(self) -> int:
        """the year that a Congressional term began"""
        return self[bg.TermFields.TERM_START]

    @property
    def end_year(self) -> int:
        """the year that a Congressional term ended"""
        return self[bg.TermFields.TERM_END]

    @property
    def position(self) -> str:
        """the position a Congress member held during the current term"""
        return self[bg.TermFields.POSITION]

    @property
    def state(self) -> str:
        """the state for which a Congress member server during the current term"""
        return self[bg.TermFields.STATE]

    @property
    def party(self) -> str:
        """the party to which a Congress member belonged during the current term"""
        return self[bg.TermFields.PARTY]


class BioguideMemberRecord(dict):
    def __init__(self, xml_data: XML.Element) -> None:
        super().__init__()
        self[bg.MemberFields.ID] = xml_data.attrib['id']
        personal_info = xml_data.find('personal-info')

        name = personal_info.find('name')
        firstnames = name.find('firstnames')
        self[bg.MemberFields.FIRST_NAME] = firstnames.text.strip()
        self[bg.MemberFields.LAST_NAME] = _fix_last_name_casing(
            name.find('lastname').text.strip())

        # TODO: parse extra details from member first name
        self[bg.MemberFields.MIDDLE_NAME] = None
        self[bg.MemberFields.NICKNAME] = None
        self[bg.MemberFields.SUFFIX] = None

        birth_year = personal_info.find('birth-year').text
        self[bg.MemberFields.BIRTH_YEAR] = \
            birth_year.strip() if birth_year and birth_year.strip() else None

        death_year = personal_info.find('death-year').text
        self[bg.MemberFields.DEATH_YEAR] = \
            death_year.strip() if death_year and death_year.strip() else None

        self[bg.MemberFields.BIOGRAPHY] = xml_data.find('biography').text

        self[bg.MemberFields.TERMS] = list()

        for t in personal_info.findall('term'):
            self[bg.MemberFields.TERMS].append(BioguideTermRecord(t))

    def __str__(self) -> str:
        return json.dumps(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BioguideMemberRecord) \
            and self.bioguide_id == o.bioguide_id \
            and self.terms == o.terms

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    @property
    def bioguide_id(self) -> str:
        """a US Congress member's Bioguide ID"""
        return self[bg.MemberFields.ID]

    @property
    def first_name(self) -> str:
        """a US Congress member's first name"""
        return self[bg.MemberFields.FIRST_NAME]

    @property
    def middle_name(self) -> str:
        """a US Congress member's middle name"""
        return self[bg.MemberFields.MIDDLE_NAME]

    @property
    def last_name(self) -> str:
        """a US Congress member's surname"""
        return self[bg.MemberFields.LAST_NAME]

    @property
    def nickname(self) -> str:
        """a US Congress member's prefered name"""
        return self[bg.MemberFields.NICKNAME]

    @property
    def suffix(self) -> str:
        """a US Congress member's name suffix"""
        return self[bg.MemberFields.SUFFIX]

    @property
    def birth_year(self) -> str:
        """a US Congress member's year of birth"""
        return self[bg.MemberFields.BIRTH_YEAR]

    @property
    def death_year(self) -> str:
        """a US Congress member's year of death"""
        return self[bg.MemberFields.DEATH_YEAR]

    @property
    def biography(self) -> str:
        """A US Congress member's biography"""
        return self[bg.MemberFields.BIOGRAPHY]

    @property
    def terms(self) -> List[BioguideTermRecord]:
        """a US Congress member's terms"""
        return self[bg.MemberFields.TERMS]


class BioguideCongressRecord(dict):
    def __init__(self, header: dict, members: List[BioguideMemberRecord]) -> None:
        super().__init__()
        self[bg.CongressFields.MEMBERS] = members
        self[bg.CongressFields.NUMBER] = header['congress']
        self[bg.CongressFields.START_YEAR] = header['start_year']
        self[bg.CongressFields.END_YEAR] = header['end_year']

    def __str__(self) -> str:
        return json.dumps(self)

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BioguideCongressRecord) \
            and self.number == o.number \
            and self.members == o.members

    def __ne__(self, o: object) -> bool:
        return not self.__ne__(o)

    @property
    def number(self) -> int:
        return self[bg.CongressFields.NUMBER]

    @property
    def start_year(self) -> int:
        return self[bg.CongressFields.START_YEAR]

    @property
    def end_year(self) -> int:
        return self[bg.CongressFields.END_YEAR]

    @property
    def members(self) -> List[BioguideMemberRecord]:
        return self[bg.CongressFields.MEMBERS]


class IncompleteHTMLResponseError(Exception):
    """Error for when essential HTML elements are missing from HTTP response text"""


def merge_bioguides(congress_records: List[BioguideCongressRecord]) -> List[BioguideMemberRecord]:
    members = list()
    processed_bioguide_ids = set()
    for congress in congress_records:
        for member in congress.members:
            if member.bioguide_id not in processed_bioguide_ids:
                members.append(member)
    return members


def get_member_bioguide_func(first_name: str, last_name: str) -> Callable[[], List[BioguideMemberRecord]]:
    def load_member_bioguide():
        return _get_bioguide_by_first_and_last_name(first_name, last_name)

    return load_member_bioguide


def get_single_bioguide_func(number_or_year: int = 1) -> Callable[[], BioguideCongressRecord]:
    def load_bioguide() -> BioguideCongressRecord:
        return _get_bioguide_by_number_or_year(number_or_year)

    return load_bioguide


def get_bioguides_range_func(start: int = 1, end: Optional[int] = None) -> Callable[[], List[BioguideCongressRecord]]:
    def load_multiple_bioguides() -> List[BioguideCongressRecord]:
        bioguides = []
        for bioguide in _congress_iter(start, end, _get_bioguide_by_number_or_year):
            bioguides.append(bioguide)

        return bioguides

    return load_multiple_bioguides


def _get_bioguide_by_first_and_last_name(first_name: str, last_name: str) -> List[BioguideMemberRecord]:
    """Get a single record for a Congress Member"""
    query = BioguideRetroQuery(last_name, first_name)

    attempts = 0
    while attempts < bg.MAX_REQUEST_ATTEMPTS:
        try:
            response = query.send()
            records = _parse_member_records(response)
            break
        except IncompleteHTMLResponseError:
            query.refresh_verification_token()
            continue

    return records


def _get_bioguide_by_number_or_year(congress: int = 1) -> BioguideCongressRecord:
    """Get a single Bioguide and clean the response"""
    if congress:
        query = BioguideRetroQuery(congress=congress)
    else:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying position corrects this
        query = BioguideRetroQuery(congress=0, position='ContCong')

    year_map = bg.CongressNumberYearMap()

    if congress >= year_map.first_valid_year:
        year_range = year_map.get_year_range_by_year(congress)
        header = {
            # max: get most recent congress
            'congress': max(year_map.get_congress_numbers(congress)),
            'start_year': year_range[0],
            'end_year': year_range[1]
        }
    else:
        header = {
            'congress': congress,
            'start_year': year_map.get_start_year(congress),
            'end_year': year_map.get_end_year(congress)
        }

    attempts = 0
    while attempts < bg.MAX_REQUEST_ATTEMPTS:
        try:
            response = query.send()
            record = _parse_congress_records(response, header)
            break
        except IncompleteHTMLResponseError:
            query.refresh_verification_token()
            continue  # reattempt query if resulting HTML is incomplete

    return record


def _congress_iter(start: int = 1, end: int = None,
                   bioguide_func: Callable[[
                       int, bool], BioguideCongressRecord] = _get_bioguide_by_number_or_year) -> Iterable[BioguideCongressRecord]:
    """A generator for looping over Congresses by number or year.
    Ranges that occur after 1785 are handled as years.
    """

    year_map = bg.CongressNumberYearMap()

    # TODO: use year_map to iterate solely by congress number

    if end > year_map.first_valid_year > start:
        raise bg.InvalidRangeError()

    # If start is a valid year
    if start > year_map.first_valid_year:  # Bioguide begins at 1786
        import datetime

        if not end:
            end = datetime.datetime.now().year

        for start_year, _ in year_map.all_congress_terms:
            if end >= start_year >= start:
                yield bioguide_func(start_year)
    else:
        if end:
            for i in range(start, end + 1):
                congress = bioguide_func(i)
                if not congress:
                    break
                yield congress
        else:
            # loop until an empty result is returned
            while start == 1000000:
                congress = bioguide_func(start)
                if not congress:
                    break
                yield congress
                start += 1


def _get_verification_token() -> str:
    root_page = requests.get(bg.BIOGUIDERETRO_ROOT_URL_STR)
    soup = BeautifulSoup(root_page.text, features='html.parser')
    verification_token_input = soup.select_one(
        'input[name="__RequestVerificationToken"]')
    return verification_token_input['value']


def _parse_member_records(response: requests.Response) -> List[BioguideMemberRecord]:
    """Stores data from a Bioguide member query as a BioguideMemberRecord"""
    bioguide_ids = _get_bioguide_ids(response.text)

    member_xml_relative_urls = set(
        bg_id[0] + '/' + bg_id + '.xml' for bg_id in bioguide_ids)

    members = list()
    failed_urls = set()

    url_count = len(member_xml_relative_urls)
    for i, relative_url in enumerate(member_xml_relative_urls):
        member_request_url = bg.BIOGUIDERETRO_MEMBER_XML_URL + relative_url
        member_response = requests.get(member_request_url)
        try:
            root = XML.fromstring(member_response.text)
            members.append(BioguideMemberRecord(root))
        except XML.ParseError:
            root = XML.fromstring(_clean_xml(member_response.text))
            members.append(BioguideMemberRecord(root))
        except requests.exceptions.ConnectionError:
            failed_urls.add(relative_url)

    for failed_url in failed_urls:
        member_response = requests.get(failed_url)
        try:
            root = XML.fromstring(member_response.text)
        except XML.ParseError:
            root = XML.fromstring(_clean_xml(member_response.text))

        members.append(BioguideMemberRecord(root))

    return members


def _parse_congress_records(response: requests.Response, header: dict) -> BioguideCongressRecord:
    """Stores data from a Bioguide congress query as a BioguideCongressRecord"""
    final_page_num = _get_final_page_number(response.text)
    cookie_jar = response.cookies
    page_num = 1

    page_response = response
    bioguide_ids = set()
    while page_num <= final_page_num:
        bioguide_ids.update(_get_bioguide_ids(page_response.text))

        if page_num == final_page_num:
            break

        page_num += 1
        page_request_url = bg.BIOGUIDERETRO_SEARCH_URL_STR + \
            '?page=' + str(page_num)
        page_response = requests.get(page_request_url, cookies=cookie_jar)

    member_xml_relative_urls = set(
        bg_id[0] + '/' + bg_id + '.xml' for bg_id in bioguide_ids)

    members = list()
    failed_urls = set()

    url_count = len(member_xml_relative_urls)
    for i, relative_url in enumerate(member_xml_relative_urls):
        member_request_url = bg.BIOGUIDERETRO_MEMBER_XML_URL + relative_url
        member_response = requests.get(member_request_url)
        try:
            root = XML.fromstring(member_response.text)
            members.append(BioguideMemberRecord(root))
        except XML.ParseError:
            root = XML.fromstring(_clean_xml(member_response.text))
            members.append(BioguideMemberRecord(root))
        except requests.exceptions.ConnectionError:
            failed_urls.add(relative_url)

    for failed_url in failed_urls:
        member_response = requests.get(failed_url)
        try:
            root = XML.fromstring(member_response.text)
        except XML.ParseError:
            root = XML.fromstring(_clean_xml(member_response.text))

        members.append(BioguideMemberRecord(root))

    return BioguideCongressRecord(header, members)


def _get_final_page_number(response_text: str) -> int:
    """Retrieves the total number of pages required to receive the full queried dataset"""
    soup = BeautifulSoup(response_text, features='html.parser')
    final_page_link = soup.select_one(
        'ul.pagination > li.page-item.PagedList-skipToLast > a.page-link')
    
    if not final_page_link:
        page_links = soup.select(
            'ul.pagination > li.page-item > a.page-link')

        final_page_link = page_links[-1]

        if final_page_link.text == '>' or final_page_link.text == '&gt;':
            final_page_link = page_links[-2]

    if not final_page_link:
        raise IncompleteHTMLResponseError(
            'Final page link was not found in pagination toolbar.')

    final_page_number = str(final_page_link['href'])\
        .split('?')[1].split('=')[1]  # parse from query string

    return int(final_page_number)


def _get_bioguide_ids(response_text: str) -> Set[str]:
    soup = BeautifulSoup(response_text, features='html.parser')
    member_links = soup.select('div.row > div > a.red')
    member_urls = [str(link['href']) for link in member_links]
    # parse from query strings
    return set(str(url.split('?')[1].split('=')[1]) for url in member_urls)


# String util functions
def _clean_xml(text: str):
    import re

    invalid_char = r'[^a-zA-Z0-9\s~`!@#$%^&*()_+=:{}[;<,>.?/\\\-\]\"\']'
    clean_text = re.sub(invalid_char, '', text)
    return clean_text


def _fix_last_name_casing(name: str) -> str:
    """Converts uppercase text to capitalized"""
    # Addresses name prefixes, like "Mc-" or "La-"
    if re.match(r'^[A-Z][a-z][A-Z]', name):
        start_pos = 3
    else:
        start_pos = 1

    capital_case = name[:start_pos] + name[start_pos:].lower()
    return capital_case
