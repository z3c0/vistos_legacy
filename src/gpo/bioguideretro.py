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

    position : str, optional
        The position of US Congress members.

    state : str, optional
        The two-letter abbreviation of a US State

    party : str, optional
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
        attempts = 0
        while True:
            try:
                response = requests.post(
                    bg.BIOGUIDERETRO_SEARCH_URL_STR, self.params)
            except requests.exceptions.ConnectionError:
                if attempts < bg.MAX_REQUEST_ATTEMPTS:
                    attempts += 1
                    continue
                else:
                    raise
            break
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

        self[bg.TermFields.POSITION] = str(
            xml_data.find('term-position').text).lower()
        self[bg.TermFields.STATE] = str(
            xml_data.find('term-state').text).upper()
        self[bg.TermFields.PARTY] = str(
            xml_data.find('term-party').text).lower()

        self[bg.TermFields.SPEAKER_OF_THE_HOUSE] = \
            self[bg.TermFields.POSITION] == 'speaker of the house'

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
    def is_house_speaker(self) -> bool:
        """a boolean flag indicating if the current member 
        held the position of Speaker of the House during the term"""
        return self[bg.TermFields.SPEAKER_OF_THE_HOUSE]

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
        # self[bg.MemberFields.MIDDLE_NAME] = None
        # self[bg.MemberFields.NICKNAME] = None
        # self[bg.MemberFields.SUFFIX] = None

        birth_year = personal_info.find('birth-year').text
        self[bg.MemberFields.BIRTH_YEAR] = \
            birth_year.strip() if birth_year and birth_year.strip() else None

        death_year = personal_info.find('death-year').text
        self[bg.MemberFields.DEATH_YEAR] = \
            death_year.strip() if death_year and death_year.strip() else None

        self[bg.MemberFields.BIOGRAPHY] = xml_data.find('biography').text

        term_records = [BioguideTermRecord(t)
                        for t in personal_info.findall('term')]
        self[bg.MemberFields.TERMS] = _merge_terms(term_records)

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

    # @property
    # def middle_name(self) -> str:
    #     """a US Congress member's middle name"""
    #     return self[bg.MemberFields.MIDDLE_NAME]

    @property
    def last_name(self) -> str:
        """a US Congress member's surname"""
        return self[bg.MemberFields.LAST_NAME]

    # @property
    # def nickname(self) -> str:
    #     """a US Congress member's prefered name"""
    #     return self[bg.MemberFields.NICKNAME]

    # @property
    # def suffix(self) -> str:
    #     """a US Congress member's name suffix"""
    #     return self[bg.MemberFields.SUFFIX]

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
        return not self.__eq__(o)

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


def merge_bioguides(congress_records: List[BioguideCongressRecord]) -> List[BioguideMemberRecord]:
    """Returns unique congress members from multiple bioguide records"""
    members = list()
    processed_bioguide_ids = set()
    for congress in congress_records:
        for member in congress.members:
            if member.bioguide_id not in processed_bioguide_ids:
                members.append(member)
                processed_bioguide_ids.add(member.bioguide_id)
    return members


def _merge_terms(term_records: List[BioguideTermRecord]) -> List[BioguideTermRecord]:
    """Returns unique congressional terms for a given member"""
    merged_terms = dict()

    for term in term_records:
        try:
            match = merged_terms[term.congress_number]
            if match.party != term.party:
                # TODO: Find way to determine current party affiliation
                match = term  # updates with most recent
                # There's nothing in the bioguide dataset to
                # indicate which party is the most recent,
                # so for now, the order by which they are
                # presented in the XML is assumed to be the
                # order by which the member was affilated
                # to each party (maybe invalidly)

            if match.is_house_speaker:
                match[bg.TermFields.POSITION] = term.position
            elif term.is_house_speaker:
                match[bg.TermFields.SPEAKER_OF_THE_HOUSE] = True

            merged_terms[term.congress_number] = match  # write changes
        except KeyError:
            merged_terms[term.congress_number] = term

    return list(merged_terms.values())


def get_members_func(first_name: str, last_name: str) -> Callable[[], List[BioguideMemberRecord]]:
    """Returns a preseeded function for retrieving data for congress members by name"""
    # Returns a list, due to there being multiple people of the same name
    def load_members() -> List[BioguideMemberRecord]:
        return _get_members_by_first_and_last_name(first_name, last_name)

    return load_members


def get_member_func(bioguide_id: str) -> Callable[[], BioguideMemberRecord]:
    """Returns a preseeded function for retreiving data for a single congress member"""

    def load_member() -> BioguideMemberRecord:
        return _get_member_by_id(bioguide_id)

    return load_member


def get_single_bioguide_func(number_or_year: int = 1) -> Callable[[], BioguideCongressRecord]:
    """Returns a preseeded function for retrieving a single congress"""
    def load_bioguide() -> BioguideCongressRecord:
        return _get_bioguide_by_number_or_year(number_or_year)

    return load_bioguide


def get_bioguides_range_func(start: int = 1, end: Optional[int] = None) -> Callable[[], List[BioguideCongressRecord]]:
    """Returns a preseeded function for retrieving multiple congresses"""
    def load_multiple_bioguides() -> List[BioguideCongressRecord]:
        bioguides = []
        for bioguide in _congress_iter(start, end, _get_bioguide_by_number_or_year):
            bioguides.append(bioguide)

        return bioguides

    return load_multiple_bioguides


def _get_member_by_id(bioguide_id: str) -> BioguideMemberRecord:
    """Get a member record corresponding to the given bioguide ID"""
    xml_relative_url = bioguide_id[0] + '/' + bioguide_id + '.xml'
    request_url = bg.BIOGUIDERETRO_MEMBER_XML_URL + xml_relative_url

    attempts = 0
    while True:
        try:
            response = requests.get(request_url)
            root = XML.fromstring(response.text)
        except XML.ParseError:
            root = XML.fromstring(_clean_xml(response.text))
        except requests.exceptions.ConnectionError:
            if attempts < bg.MAX_REQUEST_ATTEMPTS:
                # refresh session and re-attempt
                attempts += 1
                continue
            else:
                raise
        return BioguideMemberRecord(root)


def _get_members_by_first_and_last_name(first_name: str, last_name: str) -> List[BioguideMemberRecord]:
    """Get a list of member records that have a matching first and last name"""
    query = BioguideRetroQuery(last_name, first_name)
    records = _get_member_records(query)
    return records


def _get_bioguide_by_number_or_year(congress: int = 1) -> BioguideCongressRecord:
    """Get a single Bioguide and clean the response"""
    year_map = bg.CongressNumberYearMap()

    if not congress:
        congress = year_map.current_congress

    if congress > 0:
        query = BioguideRetroQuery(congress=congress)
    else:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying position corrects this
        query = BioguideRetroQuery(congress=0, position='ContCong')

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

    record = _get_congress_records(query, header)
    return record


def _congress_iter(start: int = 1, end: int = None,
                   bioguide_func: Callable[[
                       int, bool], BioguideCongressRecord] = _get_bioguide_by_number_or_year) -> Iterable[BioguideCongressRecord]:
    """A generator for looping over Congresses by number or year.
    Ranges that occur after 1785 are handled as years.
    """

    year_map = bg.CongressNumberYearMap()

    # TODO: use year_map to iterate solely by congress number

    # if the given range is interpretable as numbers or years
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
    """Fetches a session key for bioguideretro.congress.gov"""
    attempts = 0
    while True:
        try:
            root_page = requests.get(bg.BIOGUIDERETRO_ROOT_URL_STR)
        except requests.exceptions.ConnectionError:
            if attempts < bg.MAX_REQUEST_ATTEMPTS:
                attempts += 1
                continue
            else:
                raise
        break

    soup = BeautifulSoup(root_page.text, features='html.parser')
    verification_token_input = soup.select_one(
        'input[name="__RequestVerificationToken"]')
    return verification_token_input['value']


def _get_member_records(query: BioguideRetroQuery) -> List[BioguideMemberRecord]:
    """Stores data from a Bioguide member query as a BioguideMemberRecord"""
    response = query.send()
    bioguide_ids = _get_bioguide_ids(response.text)

    member_records = list()
    for bioguide_id in bioguide_ids:
        member_record = _get_member_by_id(bioguide_id)
        member_records.append(member_record)

    return member_records


def _get_congress_records(query: BioguideRetroQuery, header: dict) -> BioguideCongressRecord:
    """Stores data from a Bioguide congress query as a BioguideCongressRecord"""
    response = query.send()
    cookie_jar = response.cookies

    # use the pagination information in the response
    # to determine how many more pages of information are available
    final_page_num = _get_final_page_number(response.text)

    # then scrape the bioguide ids from the first page,
    # and loop over the remaining pages
    page_num = 1
    bioguide_ids = set()
    while page_num <= final_page_num:
        bioguide_ids.update(_get_bioguide_ids(response.text))

        if page_num == final_page_num:
            break

        page_num += 1
        page_request_url = bg.BIOGUIDERETRO_SEARCH_URL_STR + \
            '?page=' + str(page_num)

        attempts = 0
        while True:
            try:
                response = requests.get(page_request_url, cookies=cookie_jar)
            except requests.exceptions.ConnectionError:
                if attempts < bg.MAX_REQUEST_ATTEMPTS:
                    # refresh session and re-attempt
                    query.refresh_verification_token()
                    cookie_jar = (query.send()).cookies
                    attempts += 1
                    continue
                else:
                    raise
            break

    member_records = list()
    for bioguide_id in bioguide_ids:
        member_record = _get_member_by_id(bioguide_id)
        member_records.append(member_record)

    return BioguideCongressRecord(header, member_records)


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

    # negation of valid characters
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
