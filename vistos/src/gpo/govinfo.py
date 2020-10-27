"""A module for querying Gov Info data provided by the US GPO"""
import json as _json
import math as _math
import time as _time
import re as _re
import datetime as _dt
import calendar as _cal
from typing import Any, Optional, List, Callable, Dict

import requests as _requests

from vistos.src.gpo import util as _util, fields as _fields
from vistos.src.gpo.bioguideretro import BioguideMemberRecord


class GovInfoBillRecord(dict):
    """A dict-like object for handling Congressional bill
    data returned from the GovInfo API"""

    def __init__(self, bill_govinfo: dict):
        super().__init__()
        self[_fields.Bill.TITLE] = bill_govinfo['title']
        try:
            self[_fields.Bill.SHORT_TITLE] = \
                bill_govinfo['shortTitle'][0]['title']
        except (KeyError, IndexError):
            self[_fields.Bill.SHORT_TITLE] = None

        self[_fields.Bill.DATE_ISSUED] = bill_govinfo['dateIssued']
        self[_fields.Bill.PAGES] = bill_govinfo['pages']
        self[_fields.Bill.GOVERNMENT_AUTHOR] = \
            bill_govinfo['governmentAuthor2']
        self[_fields.Bill.DOC_CLASS_NUMBER] = bill_govinfo['suDocClassNumber']
        self[_fields.Bill.BILL_TYPE] = bill_govinfo['billType']
        self[_fields.Bill.BILL_VERSION] = bill_govinfo['billVersion']
        self[_fields.Bill.IS_APPROPRATION] = bill_govinfo['isAppropriation']
        self[_fields.Bill.IS_PRIVATE] = bill_govinfo['isPrivate']
        self[_fields.Bill.COMMITTEES] = bill_govinfo['committess']
        self[_fields.Bill.MEMBERS] = bill_govinfo['members']


class GovInfoCongressRecord(dict):
    """A dict-like object for handling Congressional
    directory data returned from the GovInfo API"""

    def __init__(self, number: int, start_year: int,
                 end_year: int, congress_govinfo: List[dict]):
        super().__init__()
        self[_fields.Congress.NUMBER] = number
        self[_fields.Congress.START_YEAR] = start_year
        self[_fields.Congress.END_YEAR] = end_year
        self[_fields.Congress.MEMBERS] = congress_govinfo

    @property
    def number(self) -> int:
        """The number of the given Congress0"""
        return self[_fields.Congress.NUMBER]

    @property
    def start_year(self) -> int:
        """The year the given Congress started"""
        return self[_fields.Congress.START_YEAR]

    @property
    def end_year(self) -> int:
        """The year the given Congress ended"""
        return self[_fields.Congress.END_YEAR]

    @property
    def members(self) -> List[dict]:
        """The members of the current GovInfo Congressional Directory"""
        return self[_fields.Congress.MEMBERS]


# Helper Types

GovInfoCongressList = List[GovInfoCongressRecord]
GovInfoCongressListFunc = Callable[[], GovInfoCongressList]
GovInfoMemberRecord = Dict[str, Any]
GovInfoMemberRecordFunc = \
    Callable[[BioguideMemberRecord], Optional[GovInfoMemberRecord]]
GovInfoMemberList = List[GovInfoMemberRecord]

GovInfoBillList = List[GovInfoBillRecord]
GovInfoBillListFunc = Callable[[], GovInfoBillList]


def create_cdir_func(api_key: str, congress: int) \
        -> Callable[[], Optional[GovInfoCongressRecord]]:
    """Returns a preseeded function for loading a
    specified congressional directory"""
    def govinfo_cdir_func() -> Optional[GovInfoCongressRecord]:
        return _get_cdir(api_key, congress)

    return govinfo_cdir_func


def create_member_cdir_func(api_key: str) -> GovInfoMemberRecordFunc:
    """Returns a preseeded function for loading the
    CDIR member data based on given search criteria"""
    def member_cdir_func(bioguide_member: BioguideMemberRecord) \
            -> Optional[GovInfoMemberRecord]:
        return _get_cdir_for_member(api_key, bioguide_member)

    return member_cdir_func


def create_bills_func(api_key: str, congress: int) -> GovInfoBillListFunc:
    """Returns a preseeded function for loading bills data
    based on a given Congress number"""
    def congress_bills_func() -> GovInfoBillList:
        return _get_bills(api_key, congress)

    return congress_bills_func


def check_for_govinfo(congress: int, api_key: str):
    """Check if a given Congress has GovInfo data"""
    return _cdir_exists(api_key, congress)


def _cdir_exists(api_key: str, congress: int) -> bool:
    """Returns true if a cdir package is available for the given congress"""
    packages = _packages_by_congress(api_key, congress)
    return bool(len(packages))


def _get_cdir_for_member(api_key: str, bioguide_member: BioguideMemberRecord) \
        -> Optional[GovInfoMemberRecord]:
    """Returns the biography data for the given BioguideMemberRecord"""

    # if a member dies in office, they will not be in
    # the most recent CDIR for that term
    terms = bioguide_member.terms
    if bioguide_member.death_year is not None:
        try:
            terms = [term for term in bioguide_member.terms
                     if term.end_year < int(bioguide_member.death_year)]
        except ValueError:
            # Death year may not be an int (1885c or Unknown).
            # If it's not an int, then it's unknown
            # and can't be relied on.
            # If their death year is far enough back
            # to be unknown, then they likely do not
            # have govinfo data, so no harm done
            pass

    if len(terms) == 0:
        # if all terms were excluded by the prior step, then
        # they died in their first term and they wouldn't
        # have govinfo anyways, so exit returning None
        return None

    current_congress = _util.get_current_congress_number()
    # govinfo doesn't have the CDIR of the current congress, so exclude it
    last_term = max(terms, key=lambda t: int(t.congress_number)
                    if t.congress_number != current_congress else -1)

    if not _cdir_exists(api_key, last_term.congress_number):
        # if the last term doesn't have data, then none of the preceding
        # terms can be expected to have data either, so exit returning None
        return None

    packages = \
        _packages_by_congress(api_key, last_term.congress_number)
    package_id = \
        (max(packages, key=lambda package: package['dateIssued']))['packageId']

    state_key = last_term.state
    chamber_key = 'S' if last_term.position == 'senator' else 'H'

    target_bioguide_id = bioguide_member.bioguide_id
    target_granule_id_pattern = f'^{package_id}-'
    target_granule_id_pattern += (state_key + '-' + chamber_key)
    target_granule_id_pattern += r'(-\d+)?$'

    granules = _granules(api_key, package_id)
    matching_granule = None
    while len(granules) > 0:
        granule = granules.pop()

        if granule['granuleClass'] != 'CONGRESSMEMBERSTATE':
            continue

        granule_id = granule['granuleId']

        if not _re.match(target_granule_id_pattern, granule_id):
            continue

        endpoint = \
            _granule_endpoint(api_key, package_id, granule_id)
        granule_text = _get_text_from(endpoint)
        granule_summary = _json.loads(granule_text)

        try:
            bioguide_id = granule_summary['members'][0]['bioGuideId']
        except KeyError:
            continue

        if bioguide_id != target_bioguide_id:
            continue

        matching_granule = granule_summary
        break

    return matching_granule


def _get_cdir(api_key: str, congress: int) -> Optional[GovInfoCongressRecord]:
    """Returns the congressional directory for the given congress number"""

    if not _cdir_exists(api_key, congress):
        return None

    # clear up some metadata not provided by GovInfo
    start_year, end_year = _util.get_congress_years(congress)

    # actually getting it
    #
    # To retrieve a congressional directory,
    # you must crawl through a few endpoints
    #
    # packages -> granules -> granule summaries
    #
    # GovInfo data is snapshotted as packages
    packages = _packages_by_congress(api_key, congress)
    package_id = \
        (max(packages, key=lambda package: package['dateIssued']))['packageId']

    # granules are header records within a package
    granules = _granules(api_key, package_id)

    # the details of each granule are contained within its summary
    granule_data = []
    while len(granules) > 0:
        granule = granules.pop()
        if granule['granuleClass'] != 'CONGRESSMEMBERSTATE':
            continue

        granule_id = granule['granuleId']
        endpoint = _granule_endpoint(api_key, package_id, granule_id)
        granule_text = _get_text_from(endpoint)
        granule_summary = _json.loads(granule_text)

        subgranule_classes = ('SENATOR', 'REPRESENTATIVE',
                              'DELEGATE', 'RESIDENTCOMMISSIONER')

        if granule_summary.get('subGranuleClass') in subgranule_classes:
            granule_data.append(granule_summary)

    return GovInfoCongressRecord(congress, start_year, end_year, granule_data)


def _get_bills(api_key: str, congress: int):

    packages = _bill_packages_by_congress(api_key, congress)

    bill_records = []
    for package in packages:
        package_link = package['packageLink']
        package_endpoint = f'{package_link}?api_key={api_key}'
        package_data = _get_text_from(package_endpoint)
        package_json = _json.loads(package_data)
        bill_records.append(GovInfoBillRecord(package_json))

    return bill_records


def _packages_by_congress(api_key: str, congress: int) -> List[Dict[str, Any]]:
    """Returns a list of packages for a given collection"""
    offset = 0
    page_size = 100
    pages = 1
    packages = []
    while offset < pages * page_size:
        endpoint = _collection_endpoint(api_key, 'CDIR',
                                        offset=offset,
                                        page_size=page_size,
                                        congress=str(congress))
        collection_text = _get_text_from(endpoint)
        collection = _json.loads(collection_text)
        packages = packages + collection['packages']

        package_count = int(collection['count'])
        if package_count > pages * page_size:
            pages = _math.ceil(package_count / page_size)

        offset += page_size

    return packages


def _bill_packages_by_congress(api_key: str,
                               congress: int) -> List[Dict[str, Any]]:
    """Incrementally downloads a list of bills for a given collection"""

    packages = []

    bill_doc_classes = ['hr', 's', 'hjres', 'sjres',
                        'hconres', 'sconres', 'hres',
                        'sres']

    today = _dt.datetime.now()

    # get total package count
    endpoint = \
        _collection_endpoint(api_key, 'BILLS',
                             offset=0,
                             page_size=1,
                             congress=str(congress))
    collection_text = _get_text_from(endpoint)
    collection = _json.loads(collection_text)
    total_package_count = int(collection['count'])

    year = today.year
    while total_package_count > len(packages) and year > 1700:
        window_start = _dt.datetime(year, 1, 1, 0, 0, 0)
        window_end = _dt.datetime(year, 12, 31, 23, 59, 59)

        window_start_fmt = _utc_timestamp_from_datetime(window_start)
        window_end_fmt = _utc_timestamp_from_datetime(window_end)

        for doc_class in bill_doc_classes:

            # get total package count for current doc class
            endpoint = \
                _collection_endpoint(api_key, 'BILLS',
                                     start_date=window_start_fmt,
                                     end_date=window_end_fmt,
                                     offset=0,
                                     page_size=1,
                                     congress=str(congress),
                                     doc_class=doc_class)
            collection_text = _get_text_from(endpoint)
            collection = _json.loads(collection_text)
            doc_class_package_count = int(collection['count'])

            if doc_class_package_count == 0:
                continue

            doc_class_packages = _search_for_bill_packages(0, window_start,
                                                           window_end,
                                                           api_key=api_key,
                                                           congress=congress,
                                                           doc_class=doc_class)

            packages = packages + doc_class_packages

        year -= 1

    return packages


def _search_for_bill_packages(depth, start, stop, **kwargs):
    api_key = kwargs['api_key']
    congress = kwargs['congress']
    doc_class = kwargs['doc_class']

    hierarchy = ['year', 'month', 'day', 'hour', 'minute', 'second']

    level = hierarchy[depth]

    units = None

    page_size = 100
    packages = []

    format_func = _utc_timestamp_from_datetime
    unformat_func = _utc_timestamp_to_datetime

    if level == 'year':
        months = \
            [(_dt.datetime(start.year, n, 1),
              _dt.datetime(start.year, n, _cal.monthrange(start.year, n)[1]))
             for n in range(1, 13)]

        units = [(format_func(start), format_func(stop))
                 for start, stop in months]

    elif level == 'month':
        max_day = _cal.monthrange(start.year, start.month)[1]
        days = [(start + _dt.timedelta(days=n),
                 start + _dt.timedelta(days=n + 1) - _dt.timedelta(seconds=1))
                for n in range(max_day + 1)]
        units = [(format_func(start), format_func(stop))
                 for start, stop in days]

    elif level == 'day':
        year = start.year
        month = start.month
        day = start.day
        hours = [(_dt.datetime(year, month, day, n),
                  _dt.datetime(year, month, day, n, 59, 59))
                 for n in range(24)]

        units = [(format_func(start), format_func(stop))
                 for start, stop in hours]

    elif level == 'hour':
        year = start.year
        month = start.month
        day = start.day
        hour = start.hour
        minutes = [(_dt.datetime(year, month, day, hour, n),
                    _dt.datetime(year, month, day, hour, n, 59))
                   for n in range(60)]
        units = [(format_func(start), format_func(stop))
                 for start, stop in minutes]

    elif level == 'minute':
        year = start.year
        month = start.month
        day = start.day
        hour = start.hour
        minute = start.minute
        seconds = [(_dt.datetime(year, month, day, hour, minute, n),
                    _dt.datetime(year, month, day, hour, minute, n))
                   for n in range(60)]
        units = [(format_func(start), format_func(stop))
                 for start, stop in seconds]
    elif level == 'second':
        msg = ('You shouldn\'t be seeing this - please submit an issue '
               + '@ https://github.com/z3c0/vistos/issues')
        raise Exception(msg)

    for start, stop in units:
        endpoint = _collection_endpoint(api_key, 'BILLS',
                                        offset=0,
                                        page_size=1,
                                        start_date=start,
                                        end_date=stop,
                                        congress=str(congress),
                                        doc_class=doc_class)

        collection_text = _get_text_from(endpoint)
        collection = _json.loads(collection_text)
        unit_package_count = int(collection['count'])

        if unit_package_count == 0:
            continue

        elif unit_package_count > 9999:
            start_date = unformat_func(start)
            stop_date = unformat_func(stop)
            packages = \
                packages + _search_for_bill_packages(depth + 1,
                                                     start_date,
                                                     stop_date,
                                                     api_key=api_key,
                                                     congress=congress,
                                                     doc_class=doc_class)
        else:
            offset = 0
            pages = 1
            unit_packages = []
            while offset < pages * page_size:
                endpoint = \
                    _collection_endpoint(api_key, 'BILLS',
                                         start_date=start,
                                         end_date=stop,
                                         offset=offset,
                                         page_size=page_size,
                                         congress=str(congress),
                                         doc_class=doc_class)
                collection_text = _get_text_from(endpoint)
                collection = _json.loads(collection_text)

                unit_package_count = int(collection['count'])
                if unit_package_count == 0:
                    break

                unit_packages = unit_packages + collection['packages']
                if unit_package_count > pages * page_size:
                    pages = \
                        _math.ceil(unit_package_count / page_size)

                offset += page_size

            packages = packages + unit_packages

    return packages


def _granules(api_key: str, package_id: str) -> List[dict]:
    """Returns a list of granules for a given package"""
    offset = 0
    page_size = 100
    pages = 1
    granules = []
    while offset < pages * page_size:
        endpoint = _package_granules_endpoint(api_key, package_id,
                                              offset, page_size)

        granules_text = _get_text_from(endpoint)
        granules_container = _json.loads(granules_text)
        granules = granules + granules_container['granules']

        granule_count = granules_container['count']
        if granule_count > pages * page_size:
            pages = _math.ceil(granule_count / page_size)

        offset += page_size

        # TODO: handle datasets larger than 10000
        if offset == 10000:
            break

    return granules


def _packages(api_key: str, collection_code: str) -> List[dict]:
    """Returns a list of packages for a given collection"""
    offset = 0
    page_size = 100
    pages = 1
    packages = []
    while offset < pages * page_size:
        endpoint = _collection_endpoint(api_key, collection_code,
                                        offset=offset, page_size=page_size)
        collection_text = _get_text_from(endpoint)
        collection = _json.loads(collection_text)
        packages = packages + collection['packages']

        package_count = collection['count']
        if package_count > pages * page_size:
            pages = _math.ceil(package_count / page_size)

        offset += page_size

    return packages


def _collections(api_key: str) -> List[dict]:
    """Returns a list of collections"""
    collections_text = _get_text_from(_collections_endpoint(api_key))
    collections_container = _json.loads(collections_text)
    return collections_container['collections']


# ========================== Generic API Functions ========================== #


def _get_text_from(endpoint: str) -> str:
    """Uses an HTTP GET request to retrieve text from a given endpoint"""
    response_text = None
    attempts = 0
    while True:
        try:
            response = _requests.get(_endpoint_url(endpoint))
            response_text = response.text
            break
        except _requests.exceptions.ConnectionError:
            if attempts < _util.MAX_REQUEST_ATTEMPTS:
                attempts += 1
                _time.sleep(2 * attempts)
                continue
            raise

    return response_text


def _collections_endpoint(api_key: str) -> str:
    """Creates an endpoint for retrieving a list of available collections"""
    return '/collections' + _query_string(api_key=api_key)


def _collection_endpoint(api_key: str,
                         collection: str,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         offset: int = 0,
                         page_size: int = 100,
                         congress: Optional[str] = None,
                         doc_class: Optional[str] = None) -> str:
    """Creates an endpoint for retrieving a collection"""
    if not start_date:
        start_date = _utc_timestamp_from_parts(1700, 1, 1)

    if not end_date:
        end_date = _current_datetime()

    query_params = {'api_key': api_key,
                    'offset': offset,
                    'pageSize': page_size}

    # zero is a valid congress
    # so check for None explicitly
    if congress is not None:
        query_params['congress'] = congress

    if doc_class:
        query_params['docClass'] = doc_class

    query_string = _query_string(**query_params)

    endpoint = (f'/collections/{collection}' +
                f'/{start_date}/{end_date}')

    return endpoint + query_string


def _package_summary_endpoint(api_key: str, package_id: str) -> str:
    """Creates an endpoint for retrieving a given package's summary"""
    return f'/packages/{package_id}/summary{_query_string(api_key=api_key)}'


def _package_endpoint(api_key: str, package_id: str, content_type: str) -> str:
    """Creates an endpoint for retrieving a given package's content
    in the format specified by the content type"""
    endpoint = (f'/packages/{package_id}' +
                f'/{content_type}' +
                _query_string(api_key=api_key))
    return endpoint


def _package_granules_endpoint(api_key: str,
                               package_id: str,
                               offset: int = 0,
                               page_size: int = 100) -> str:
    """Creates an endpoint for retrieving a given package's summary"""
    kwargs = {
        'api_key': api_key,
        'offset': offset,
        'pageSize': page_size
    }

    query_string = _query_string(**kwargs)
    return f'/packages/{package_id}/granules{query_string}'


def _granule_endpoint(api_key: str, package_id: str, granule_id: str) -> str:
    """Creates an endpoint for retrieving a given granule's summary"""
    endpoint = (f'/packages/{package_id}' +
                f'/granules/{granule_id}/summary' +
                _query_string(api_key=api_key))

    return endpoint


def _granule_content_endpoint(api_key: str, package_id: str,
                              granule_id: str, content_type: str) -> str:
    """Creates an endpoint for retrieving a given granule's content
    in the format specified by the content type"""
    endpoint = f'/packages/{package_id}/granules/{granule_id}/{content_type}'
    query_string = _query_string(api_key=api_key)
    return endpoint + query_string


def _endpoint_url(endpoint) -> str:
    """Creates a URL endpoint based on the path given"""
    return _util.GOVINFO_API_URL_STR + endpoint


def _query_string(**kwargs) -> str:
    """Creates a query string from given keywords"""
    args = kwargs.items()
    return '?' + ('&'.join([key + '=' + str(val) for key, val in args]))


def _current_datetime() -> str:
    """Returns the current time formatted as yyyy-MM-ddThh:mm:ssZ"""
    now = _dt.datetime.now()
    return _utc_timestamp_from_parts(now.year, now.month, now.day,
                                     now.hour, now.minute, now.second)


def _utc_timestamp_from_datetime(dt: _dt.datetime) -> str:
    return _utc_timestamp_from_parts(*_datetime_to_parts(dt))


def _utc_timestamp_to_datetime(utc_timestamp: str) -> _dt.datetime:
    date, time_str = utc_timestamp.replace('Z', '').split('T')
    year, month, day = date.split('-')
    hour, minute, second = time_str.split(':')
    return _dt.datetime(int(year), int(month), int(day),
                        int(hour), int(minute), int(second))


def _datetime_to_parts(dt: _dt.datetime):
    return (dt.year, dt.month, dt.day,
            dt.hour, dt.minute, dt.second)


def _utc_timestamp_from_parts(year: int, month: int, day: int,
                              hour: int = 0, minute: int = 0,
                              second: int = 0) -> str:
    """Returns a date/time formatted as yyyy-MM-ddThh:mm:ssZ"""
    return f'{year}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z'


def _utc_timestamp_to_int(datetime_str: str) -> int:
    """Converts a datetime from yyyy-MM-ddThh:mm:ssZ to yyyyMMddhhmmss"""
    date, time_str = datetime_str.replace('Z', '').split('T')
    year, month, day = date.split('-')
    hour, minute, second = time_str.split(':')
    return int(year + month + day + hour + minute + second)
