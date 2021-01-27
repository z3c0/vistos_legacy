"""A module for querying Bioguide data provided by the US GPO"""

import json as _json
import time as _time
import re as _re
import sys as _sys
from typing import List, Optional, Callable
from defusedxml import ElementTree as _XML
from queue import PriorityQueue
from threading import Thread

import requests as _requests
from bs4 import BeautifulSoup as _BeautifulSoup

from vistos.src.gpo import (error as _error,
                            index as _index,
                            util as _util,
                            fields as _fields,
                            option as _option)


class BioguideRetroQuery:
    """Object for sending HTTP POST requests to bioguideretro.congress.gov"""

    def __init__(self, last_name: Optional[str] = None,
                 first_name: Optional[str] = None,
                 position: Optional[str] = None,
                 state: Optional[str] = None,
                 party: Optional[str] = None,
                 congress: Optional[int] = None):

        self.last_name = last_name
        self.first_name = first_name
        self.position = position
        self.state = state
        self.party = party
        self.year_or_congress = congress
        self.verification_token = _get_verification_token()

    def send(self) -> _requests.Response:
        """Sends an HTTP POST request to bioguide.congress.gov,
        returning the resulting HTML text"""
        attempts = 0
        while True:
            try:
                url = _util.BIOGUIDERETRO_SEARCH_URL_STR
                response = _requests.post(url, self.params)
            except _requests.exceptions.ConnectionError as err:
                if attempts < _util.MAX_REQUEST_ATTEMPTS:
                    attempts += 1
                    continue
                raise _error.BioguideConnectionError() from err
            break
        return response

    def refresh_verification_token(self) -> None:
        """Fetches a new verification token"""
        self.verification_token = _get_verification_token()

    @property
    def params(self) -> dict:
        """Returns query parameters as a dictionary"""
        return {'LastName': self.last_name,
                'FirstName': self.first_name,
                'Position': self.position,
                'State': self.state,
                'Party': self.party,
                'YearOrCongress': self.year_or_congress,
                'submitButton': 'submit',
                '__RequestVerificationToken': self.verification_token}


class BioguideTermRecord(dict):
    """A dict-like object for storing term details"""

    def __init__(self, congress_number, party, position, state) -> None:
        super().__init__()
        self[_fields.Term.CONGRESS_NUMBER] = congress_number

        self[_fields.Term.TERM_START] = \
            _util.get_start_year(congress_number)
        self[_fields.Term.TERM_END] = \
            _util.get_end_year(congress_number)

        self[_fields.Term.POSITION] = position
        self[_fields.Term.STATE] = state
        self[_fields.Term.PARTY] = party

        self[_fields.Term.SPEAKER_OF_THE_HOUSE] = \
            self[_fields.Term.POSITION] == 'speaker of the house'

    def __str__(self) -> str:
        return self.to_json()

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

    def to_json(self):
        """Returns the current term as a JSON string"""
        return _json.dumps(self)

    @property
    def congress_number(self) -> int:
        """a Congressional term's number"""
        return self[_fields.Term.CONGRESS_NUMBER]

    @property
    def start_year(self) -> int:
        """the year that a Congressional term began"""
        return self[_fields.Term.TERM_START]

    @property
    def end_year(self) -> int:
        """the year that a Congressional term ended"""
        return self[_fields.Term.TERM_END]

    @property
    def position(self) -> str:
        """the position a Congress member held during the current term"""
        return self[_fields.Term.POSITION]

    @property
    def is_house_speaker(self) -> bool:
        """a boolean flag indicating if the current member
        held the position of Speaker of the House during the term"""
        return self[_fields.Term.SPEAKER_OF_THE_HOUSE]

    @property
    def state(self) -> str:
        """the state for which a Congress member
        served during the current term"""
        return self[_fields.Term.STATE]

    @property
    def party(self) -> str:
        """the party to which a Congress member
        belonged during the current term"""
        return self[_fields.Term.PARTY]


class BioguideTermList(list):
    """A list-based class for handling multiple BioguideTermRecords"""

    def __init__(self, term_list: List[BioguideTermRecord]):
        super().__init__()
        for term in term_list:
            self.append(term)

    def __str__(self):
        return self.to_json()

    def to_json(self) -> str:
        """Returns the current member list as a JSON string"""
        return _json.dumps(self)


class BioguideMemberRecord(dict):
    """A class for handing bioguide member data"""

    def __init__(self, xml_data) -> None:
        super().__init__()
        self[_fields.Member.ID] = xml_data.attrib['id']
        personal_info = xml_data.find('personal-info')

        name = personal_info.find('name')
        self[_fields.Member.LAST_NAME] = \
            _util.Text.fix_last_name_casing(name.find('lastname').text.strip())

        firstnames = name.find('firstnames')
        first_name = firstnames.text.strip()

        # parse suffixes like Jr, Sr, III etc from
        # the first name to enable easier concatenation
        # into a formatted whole name further downstream
        suffix_pattern = r',? (Jr\.?|Sr\.?|IV|I{1,3})'
        suffix_match = _re.search(suffix_pattern, first_name)
        if suffix_match:
            self[_fields.Member.SUFFIX] = suffix_match.group(1)
            first_name = _re.sub(suffix_pattern, '', first_name)
        else:
            self[_fields.Member.SUFFIX] = None

        nickname_pattern = r' \(([\w\. ]+)\)'
        nickname_match = _re.search(nickname_pattern, first_name)
        if nickname_match:
            self[_fields.Member.NICKNAME] = nickname_match.group(1)
            first_name = _re.sub(nickname_pattern, '', first_name)
        else:
            self[_fields.Member.NICKNAME] = None

        self[_fields.Member.FIRST_NAME] = first_name

        birth_year = personal_info.find('birth-year').text
        self[_fields.Member.BIRTH_YEAR] = \
            birth_year.strip() if birth_year and birth_year.strip() else None

        death_year = personal_info.find('death-year').text
        self[_fields.Member.DEATH_YEAR] = \
            death_year.strip() if death_year and death_year.strip() else None

        biography = xml_data.find('biography').text
        if biography is not None:
            self[_fields.Member.BIOGRAPHY] = \
                biography.strip().replace('\n', '')
        else:
            self[_fields.Member.BIOGRAPHY] = None

        term_records = []
        for term in personal_info.findall('term'):
            try:
                congress_number = int(str(term.find('congress-number').text))
            except AttributeError:
                continue

            party = term.find('term-party').text
            if party == 'NA' or (party and party.strip() == ''):
                party = None
            else:
                party = str(party).lower()

            position = str(term.find('term-position').text).lower()
            state = str(term.find('term-state').text).upper()
            term_records.append(BioguideTermRecord(congress_number, party,
                                                   position, state))

        self[_fields.Member.TERMS] = _merge_terms(term_records)

    def __str__(self) -> str:
        return self.to_json()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BioguideMemberRecord) \
            and self.bioguide_id == o.bioguide_id \
            and self.terms == o.terms

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def to_json(self) -> str:
        """Returns the current member as a JSON string"""
        return _json.dumps(self)

    @property
    def bioguide_id(self) -> str:
        """a US Congress member's Bioguide ID"""
        return self[_fields.Member.ID]

    @property
    def first_name(self) -> str:
        """a US Congress member's first name"""
        return self[_fields.Member.FIRST_NAME]

    @property
    def last_name(self) -> str:
        """a US Congress member's surname"""
        return self[_fields.Member.LAST_NAME]

    @property
    def nickname(self) -> str:
        """a US Congress member's prefered name"""
        return self[_fields.Member.NICKNAME]

    @property
    def suffix(self) -> str:
        """a US Congress member's name suffix"""
        return self[_fields.Member.SUFFIX]

    @property
    def birth_year(self) -> str:
        """a US Congress member's year of birth"""
        return self[_fields.Member.BIRTH_YEAR]

    @property
    def death_year(self) -> str:
        """a US Congress member's year of death"""
        return self[_fields.Member.DEATH_YEAR]

    @property
    def biography(self) -> str:
        """A US Congress member's biography"""
        return self[_fields.Member.BIOGRAPHY]

    @property
    def terms(self) -> BioguideTermList:
        """a US Congress member's terms"""
        return self[_fields.Member.TERMS]


class BioguideMemberRecords(dict):
    """a dict-based class for handling multiple members"""

    def __init__(self, members_list: List[BioguideMemberRecord]):
        super().__init__()
        for member in members_list:
            self[member.bioguide_id] = member

    def __str__(self):
        return self.to_json()

    def to_json(self) -> str:
        """Returns the current collection of members as JSON"""
        return _json.dumps(self)

    def to_list(self) -> List[BioguideMemberRecord]:
        """Returns the current collection of members
        as a BioguideMemberList object"""
        return BioguideMemberList(list(self.values()))


class BioguideMemberList(list):
    """A list-based class for handling multiple BioguideConressRecords"""

    def __init__(self, member_list: List[BioguideMemberRecord]):
        super().__init__()
        for member in member_list:
            self.append(member)

    def __str__(self):
        return self.to_json()

    def to_json(self) -> str:
        """Returns the current member list as a JSON string"""
        return _json.dumps(self)

    def to_records(self) -> BioguideMemberRecords:
        """Returns the current member list as a CongressMemberRecords object"""
        return BioguideMemberRecords(self)


class BioguideCongressRecord(dict):
    """A class for grouping BioguideMemberList byy congress"""

    def __init__(self, congress_number: int, members: BioguideMemberList):
        super().__init__()

        if congress_number >= _util.first_valid_year():
            year_range = _util.get_year_range_by_year(congress_number)
            self[_fields.Congress.NUMBER] = \
                max(_util.get_congress_numbers(congress_number))
            self[_fields.Congress.START_YEAR] = year_range[0]
            self[_fields.Congress.END_YEAR] = year_range[1]
        else:
            self[_fields.Congress.NUMBER] = congress_number
            self[_fields.Congress.START_YEAR] = \
                _util.get_start_year(congress_number)
            self[_fields.Congress.END_YEAR] = \
                _util.get_end_year(congress_number)

        self[_fields.Congress.MEMBERS] = members

    def __str__(self) -> str:
        return self.to_json()

    def __eq__(self, o: object) -> bool:
        return isinstance(o, BioguideCongressRecord) \
            and self.number == o.number \
            and self.members == o.members

    def __ne__(self, o: object) -> bool:
        return not self.__eq__(o)

    def to_json(self) -> str:
        """Returns the current congress as a JSON string"""
        return _json.dumps(self)

    @property
    def number(self) -> int:
        """congress number"""
        return self[_fields.Congress.NUMBER]

    @property
    def start_year(self) -> int:
        """The year the given congress started"""
        return self[_fields.Congress.START_YEAR]

    @property
    def end_year(self) -> int:
        """The year the given congress ended"""
        return self[_fields.Congress.END_YEAR]

    @property
    def members(self) -> BioguideMemberList:
        """A list of congress members belonging to the given congress"""
        return self[_fields.Congress.MEMBERS]


# Types Aliases
BioguideMembersFunc = Callable[[], BioguideMemberList]
BioguideMemberFunc = Callable[[], BioguideMemberRecord]
BioguideCongressFunc = Callable[[], BioguideCongressRecord]


# Bioguide Functions

def create_bioguide_members_func(fname: str = None, lname: str = None,
                                 pos: str = None, party: str = None,
                                 state: str = None,
                                 congress: int = None) -> BioguideMembersFunc:
    """Returns a preseeded function for retrieving data
    for congress members by name or position"""
    # Returns a list, due to there being multiple people of the same name
    def load_members() -> BioguideMemberList:
        return _query_members(fname, lname, pos, party, state, congress)

    return load_members


def create_bioguide_member_func(bioguide_id: str) -> BioguideMemberFunc:
    """Returns a preseeded function for retreiving data
     for a single congress member"""

    def load_member() -> BioguideMemberRecord:
        return _query_member_by_id(bioguide_id)

    return load_member


def create_bioguide_func(number: int = 1) -> BioguideCongressFunc:
    """Returns a preseeded function for retrieving a single congress"""
    def load_bioguide() -> BioguideCongressRecord:
        return _query_bioguide_by_number(number)

    return load_bioguide


def _merge_terms(term_records: BioguideTermList) -> BioguideTermList:
    """Returns unique congressional terms for a given member"""
    merged_terms = dict()

    for term in term_records:
        if term.position in ('vice president', 'president'):
            continue

        try:
            match = merged_terms[term.congress_number]

            # if a duplicate term exists, merge the details
            if match.party != term.party:
                match = term  # updates with most recent
                # There's nothing in the bioguide dataset to
                # indicate which party is the most recent,
                # so for now, the order by which they are
                # presented in the XML is assumed to be the
                # order by which the member was affilated
                # to each party (maybe invalidly)

            if match.is_house_speaker:
                # shed "speaker of the house" in
                # favor of the actual position
                # (really only representative)
                match[_fields.Term.POSITION] = term.position
            elif term.is_house_speaker:
                # if current record is house speaker
                # flag the existing record as house speaker
                match[_fields.Term.SPEAKER_OF_THE_HOUSE] = True

            merged_terms[term.congress_number] = match  # write changes
        except KeyError:
            merged_terms[term.congress_number] = term

    return BioguideTermList(merged_terms.values())


def _query_member_by_id(bioguide_id: str) -> BioguideMemberRecord:
    """Get a member record corresponding to the given bioguide ID"""
    xml_relative_url = bioguide_id[0] + '/' + bioguide_id + '.xml'
    request_url = _util.BIOGUIDERETRO_MEMBER_XML_URL + xml_relative_url

    member_record = None
    attempts = 0
    while True:
        try:
            response = _requests.get(request_url)
        except _requests.exceptions.ConnectionError as err:
            if attempts < _util.MAX_REQUEST_ATTEMPTS:
                attempts += 1
                _time.sleep(2 * attempts)
                continue
            raise _error.BioguideConnectionError() from err

        try:
            xml_root = _XML.fromstring(response.text)
            member_record = BioguideMemberRecord(xml_root)
            break
        except _XML.ParseError:
            xml_root = _XML.fromstring(_util.Text.clean_xml(response.text))
            member_record = BioguideMemberRecord(xml_root)

        break  # just in case

    return member_record


def _query_members_by_id(bioguide_ids: list) -> BioguideMemberList:
    """Gets a BioguideMemberList object corresponding
    to the given list of bioguide IDs"""
    member_records = list()

    threading = True

    def _get_members_concurrently():
        while threading:
            bioguide_id = q.get()
            if bioguide_id != 0:
                member_record = _query_member_by_id(bioguide_id)
                member_records.append(member_record)
                q.task_done()

    q = PriorityQueue(_util.NUMBER_OF_THREADS * 2)
    for _ in range(_util.NUMBER_OF_THREADS):
        t = Thread(target=_get_members_concurrently)
        t.daemon = True
        t.start()

    try:
        for bioguide_id in bioguide_ids:
            q.put(bioguide_id)

        q.join()
    except KeyboardInterrupt:
        _sys.exit(1)

    # clean up threads
    threading = False
    for _ in range(_util.NUMBER_OF_THREADS):
        q.put(0)

    return BioguideMemberList(member_records)


def _query_members(fname: str = None, lname: str = None,
                   pos: str = None, party: str = None,
                   state: str = None,
                   congress: int = None) -> BioguideMemberList:
    """Get a list of member records that match the given criteria"""
    if pos is not None and not _option.is_valid_bioguide_position(pos):
        raise _error.InvalidPositionError(pos)

    if party is not None and not _option.is_valid_bioguide_party(party):
        raise _error.InvalidPartyError(party)

    if state is not None and not _option.is_valid_bioguide_state(state):
        raise _error.InvalidStateError(state)

    if congress is not None and not _util.is_valid_number(congress):
        raise _error.InvalidCongressError(congress)

    query = BioguideRetroQuery(lname, fname, pos, state, party, congress)
    bioguide_ids = _scrape_bioguide_ids(query)
    records = _get_member_records(bioguide_ids)
    return records


def _query_bioguide_by_number(congress_number: int = 1, scrape: bool = False) \
        -> BioguideCongressRecord:
    """Get a single Bioguide and clean the response"""
    if not scrape and _index.exists_in_congress_index(congress_number):
        bioguide_ids = _index.lookup_bioguide_ids(congress_number)
    else:
        bioguide_ids = _scrape_congress_bioguide_ids(congress_number)

    members = _query_members_by_id(bioguide_ids)
    record = BioguideCongressRecord(congress_number, members)
    return record


def _get_verification_token() -> str:
    """Fetches a session key for bioguideretro.congress.gov"""
    root_page = _requests.get(_util.BIOGUIDERETRO_ROOT_URL_STR)
    soup = _BeautifulSoup(root_page.text, features='html.parser')
    verification_token_input = \
        soup.select_one('input[name="__RequestVerificationToken"]')
    return verification_token_input['value']


def _get_member_records(bioguide_ids: List[str]) -> BioguideMemberList:
    """Stores data from a Bioguide member query as a BioguideMemberList"""
    member_records = list()
    for bioguide_id in bioguide_ids:
        member_record = _query_member_by_id(bioguide_id)
        member_records.append(member_record)

    return BioguideMemberList(member_records)


def _scrape_congress_bioguide_ids(congress: int = 1) -> List[str]:
    """Stores data from a Bioguide congressquery as a
    BioguideCongressRecord"""

    position = None
    if congress == 0:
        # Querying congress 0 includes congress-members-turned-president
        # Specifying position corrects this
        position = 'ContCong'
        query = BioguideRetroQuery(congress=congress, position=position)
        bioguide_ids = _scrape_bioguide_ids(query)

        position = 'Delegate'
        query = BioguideRetroQuery(congress=congress, position=position)
        bioguide_ids = bioguide_ids + _scrape_bioguide_ids(query)

    elif congress is None:
        congress = _util.get_current_congress_number()
        query = BioguideRetroQuery(congress=congress)
        bioguide_ids = _scrape_bioguide_ids(query)

    else:
        query = BioguideRetroQuery(congress=congress)
        bioguide_ids = _scrape_bioguide_ids(query)

    return bioguide_ids


def _scrape_bioguide_ids(query: BioguideRetroQuery) -> List[str]:
    response = query.send()
    cookie_jar = response.cookies

    # use the pagination information in the response
    # to determine how many more pages of information are available
    final_page_num = _get_final_page_number(response.text)

    # then scrape the bioguide ids from the first page,
    # and loop over the remaining pages
    page_num = 1
    bioguide_ids = list()
    while page_num <= final_page_num:
        soup = _BeautifulSoup(response.text, features='html.parser')
        member_links = soup.select('div.row > div > a.red')
        member_urls = [str(link['href']) for link in member_links]

        # Parse Bioguide IDs from query string of member urls
        bioguide_ids = bioguide_ids + list(str(url.split('?')[1].split('=')[1])
                                           for url in member_urls)

        if page_num == final_page_num:
            break

        page_num += 1
        page_request_url = _util.BIOGUIDERETRO_SEARCH_URL_STR + \
            '?page=' + str(page_num)

        attempts = 0
        while True:
            try:
                response = _requests.get(page_request_url, cookies=cookie_jar)
            except _requests.exceptions.ConnectionError as err:
                if attempts < _util.MAX_REQUEST_ATTEMPTS:
                    # refresh session and re-attempt
                    query.refresh_verification_token()
                    cookie_jar = (query.send()).cookies
                    attempts += 1
                    continue
                raise _error.BioguideConnectionError() from err
            break

    return bioguide_ids


def _get_final_page_number(response_text: str) -> int:
    """Retrieves the total number of pages required to receive the full
    queried dataset"""
    soup = _BeautifulSoup(response_text, features='html.parser')
    final_page_ref = \
        'ul.pagination > li.page-item.PagedList-skipToLast > a.page-link'
    final_page_link = soup.select_one(final_page_ref)

    if not final_page_link:
        page_ref = 'ul.pagination > li.page-item > a.page-link'
        page_links = soup.select(page_ref)

        if len(page_links) > 0:
            final_page_link = page_links[-1]

            if final_page_link.text == '>' or final_page_link.text == '&gt;':
                final_page_link = page_links[-2]

    if final_page_link:
        final_page_number = str(final_page_link['href'])\
            .split('?')[1].split('=')[1]  # parse from query string
    else:
        # default to one for single-page results
        final_page_number = 1

    return int(final_page_number)
