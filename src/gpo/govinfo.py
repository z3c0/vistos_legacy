"""A module for querying Gov Info data provided by the US GPO"""
import sys
import datetime
import json
import math
import time

from typing import Optional, List, Callable

import requests

from quinque.src.gpo import util, fields


class GovInfoCongressRecord(dict):
    """A dict-like object for handling datasets returned from the GovInfo API"""

    def __init__(self, number: int, start_year: int,
                 end_year: int, govinfo: List[dict]):
        super().__init__()
        self[fields.Congress.NUMBER] = number
        self[fields.Congress.START_YEAR] = start_year
        self[fields.Congress.END_YEAR] = end_year
        self[fields.Congress.MEMBERS] = govinfo

    @property
    def number(self) -> int:
        """The number of the given Congress0"""
        return self[fields.Congress.NUMBER]

    @property
    def start_year(self) -> int:
        """The year the given Congress started"""
        return self[fields.Congress.START_YEAR]

    @property
    def end_year(self) -> int:
        """The year the given Congress ended"""
        return self[fields.Congress.END_YEAR]

    @property
    def members(self) -> List[dict]:
        """The members of the current GovInfo Congressional Directory"""
        return self[fields.Congress.MEMBERS]


def create_multi_govinfo_cdir_func(api_key: str, congress_numbers: List[int]) \
        -> Callable[[], List[GovInfoCongressRecord]]:
    """Returns a preseeded function for loading multiple congressional directories"""
    def multi_govinfo_cdir_func() -> List[GovInfoCongressRecord]:
        govinfo_list = []

        for congress in congress_numbers:
            govinfo = _get_congressional_directory(api_key, congress)
            govinfo_list.append(govinfo)
        return govinfo_list

    return multi_govinfo_cdir_func


def create_verbose_multi_govinfo_cdir_func(api_key: str, congress_numbers: List[int]) \
        -> Callable[[], List[GovInfoCongressRecord]]:
    """Returns a preseeded function for loading multiple congressional directories"""
    def verbose_multi_govinfo_cdir_func() -> List[GovInfoCongressRecord]:
        govinfo_list = []

        for congress in congress_numbers:
            govinfo = _get_congressional_directory_verbose(api_key, congress)
            govinfo_list.append(govinfo)
        return govinfo_list

    return verbose_multi_govinfo_cdir_func


def create_govinfo_cdir_func(api_key: str, congress: int) -> Callable[[], List[dict]]:
    """Returns a preseeded function for loading a specified congressional directory"""
    def govinfo_cdir_func() -> List[dict]:
        return _get_congressional_directory(api_key, congress)

    return govinfo_cdir_func


def create_verbose_govinfo_cdir_func(api_key: str, congress: int) -> Callable[[], List[dict]]:
    """Returns a preseeded function for loading a specified congressional directory"""
    def verbose_govinfo_cdir_func() -> List[dict]:
        return _get_congressional_directory_verbose(api_key, congress)

    return verbose_govinfo_cdir_func


def check_if_cdir_exists(api_key: str, congress: int) -> bool:
    """Returns true if a cdir package is available for the given congress"""
    packages = _packages_by_congress(api_key, 'CDIR', congress)
    return bool(len(packages))


def _get_congressional_directory(api_key: str, congress: int) -> GovInfoCongressRecord:
    """Returns the congressional directory for the given congress number"""
    # Any updates done here must also be done in _get_congressional_directory_verbose()

    # clear up some metadata not provided by GovInfo
    year_map = util.CongressNumberYearMap()
    start_year, end_year = year_map.get_congress_years(congress)

    # what we're getting from GovInfo
    target_class = 'CONGRESSMEMBERSTATE'
    target_sub_classes = \
        {'SENATOR', 'REPRESENTATIVE', 'DELEGATE', 'RESIDENTCOMMISSIONER'}

    # actually getting it
    #
    # To retrieve a congressional directory,
    # you must crawl through a few endpoints
    #
    # packages -> granules -> granule summaries
    #
    # GovInfo data is snapshotted as packages
    packages = _packages_by_congress(api_key, 'CDIR', congress)
    package_id = \
        (max(packages, key=lambda package: package['dateIssued']))['packageId']

    # granules are header records within a package
    granules = _granules(api_key, package_id)

    # the details of each granule are contained within its summary
    granule_summaries = []
    for granule in granules:
        if granule['granuleClass'] == target_class:
            endpoint = \
                _granule_summary_endpoint(
                    api_key, package_id, granule['granuleId'])
            granule_text = _get_text_from(endpoint)
            granule_summary = json.loads(granule_text)

            if granule_summary.get('subGranuleClass') in target_sub_classes:
                granule_summaries.append(granule_summary)

    return GovInfoCongressRecord(congress, start_year, end_year, granule_summaries)


def _get_congressional_directory_verbose(api_key: str, congress: int) -> GovInfoCongressRecord:
    """Returns the congressional directory for the given congress number"""
    # Any updates done here must also be done in _get_congressional_directory()

    # clear up some metadata not provided by GovInfo
    year_map = util.CongressNumberYearMap()
    start_year, end_year = year_map.get_congress_years(congress)

    # what we're getting from GovInfo
    target_class = 'CONGRESSMEMBERSTATE'
    target_sub_classes = \
        {'SENATOR', 'REPRESENTATIVE', 'DELEGATE', 'RESIDENTCOMMISSIONER'}

    # actually getting it
    #
    # To retrieve a congressional directory,
    # you must crawl through a few endpoints
    #
    # packages -> granules -> granule summaries
    #
    # GovInfo data is snapshotted as packages

    print(f'Querying GovInfo CDIR records for Congress {congress}')

    packages = _packages_by_congress(api_key, 'CDIR', congress)
    package_id = \
        (max(packages, key=lambda package: package['dateIssued']))['packageId']

    print(f'Downloading granules for package {package_id}')

    # granules are header records within a package
    granules = _granules(api_key, package_id)

    print(f'Downloading granule summaries')
    # the details of each granule are contained within its summary
    granule_summaries = []

    try:
        total_records = len(granules)
        complete = 0
        for granule in granules:
            if granule['granuleClass'] == target_class:
                endpoint = \
                    _granule_summary_endpoint(
                        api_key, package_id, granule['granuleId'])
                granule_text = _get_text_from(endpoint)
                granule_summary = json.loads(granule_text)

                if granule_summary.get('subGranuleClass') in target_sub_classes:
                    granule_summaries.append(granule_summary)

            complete += 1
            print(f'{int((complete / total_records) * 100)}% downloaded\r', end='')
        print('\nDownload complete')
    except (KeyboardInterrupt, SystemExit):
        print('\nDownload interrupted')
        sys.exit()
    except requests.exceptions.ConnectionError as conn_err:
        print(f'\nDownload failed: {conn_err}')
        sys.exit()

    return GovInfoCongressRecord(congress, start_year, end_year, granule_summaries)


def _packages_by_congress(api_key: str, collection_code: str, congress: int) -> List[dict]:
    """Returns a list of packages for a given collection"""
    offset = 0
    page_size = 100
    pages = 1
    packages = []
    while offset < pages * page_size:
        endpoint = _collection_endpoint(api_key, collection_code,
                                        offset=offset, page_size=page_size, congress=congress)
        collection_text = _get_text_from(endpoint)
        collection = json.loads(collection_text)
        packages = packages + collection['packages']

        package_count = collection['count']
        if package_count > pages * page_size:
            pages = math.ceil(package_count / page_size)

        offset += page_size

    return packages


def _granules(api_key: str, package_id: str) -> List[dict]:
    """Returns a list of granules for a given package"""
    offset = 0
    page_size = 100
    pages = 1
    granules = []
    while offset < pages * page_size:
        endpoint = _granules_endpoint(api_key, package_id, offset, page_size)
        granules_text = _get_text_from(endpoint)
        granules_container = json.loads(granules_text)
        granules = granules + granules_container['granules']

        granule_count = granules_container['count']
        if granule_count > pages * page_size:
            pages = math.ceil(granule_count / page_size)

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
        collection = json.loads(collection_text)
        packages = packages + collection['packages']

        package_count = collection['count']
        if package_count > pages * page_size:
            pages = math.ceil(package_count / page_size)

        offset += page_size

    return packages


def _collections(api_key: str) -> List[dict]:
    """Returns a list of collections"""
    collections_text = _get_text_from(_collections_endpoint(api_key))
    collections_container = json.loads(collections_text)
    return collections_container['collections']


##################################### Generic API Functions ########################################


def _get_text_from(endpoint: str) -> str:
    """Uses an HTTP GET request to retrieve text from a given endpoint"""
    response_text = None
    attempts = 0
    while True:
        try:
            response = requests.get(_endpoint_url(endpoint))
            response_text = response.text
            break
        except requests.exceptions.ConnectionError:
            if attempts < util.MAX_REQUEST_ATTEMPTS:
                attempts += 1
                time.sleep(2)
                continue
            raise

    return response_text


def _collections_endpoint(api_key: str) -> str:
    """Creates an endpoint for retrieving a list of available collections"""
    return '/collections' + _query_string(api_key=api_key)


def _collection_endpoint(api_key: str,
                         collection: str,
                         last_modified_start_date: Optional[str] = None,
                         last_modified_end_date: Optional[str] = None,
                         offset: int = 0,
                         page_size: int = 100,
                         congress: Optional[str] = None,
                         doc_class: Optional[str] = None) -> str:
    """Creates an endpoint for retrieving a collection"""
    if not last_modified_start_date:
        last_modified_start_date = _datetime_from_parts(1970, 1, 1)

    if not last_modified_end_date:
        last_modified_end_date = _current_datetime()

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

    endpoint = f'/collections/{collection}/{last_modified_start_date}/{last_modified_end_date}'

    return endpoint + query_string


def _package_summary_endpoint(api_key: str, package_id: str) -> str:
    """Creates an endpoint for retrieving a given package's summary"""
    return f'/packages/{package_id}/summary{_query_string(api_key=api_key)}'


def _package_content_endpoint(api_key: str, package_id: str, content_type: str) -> str:
    """Creates an endpoint for retrieving a given package's content
    in the format specified by the content type"""
    return f'/packages/{package_id}/{content_type}{_query_string(api_key=api_key)}'


def _granules_endpoint(api_key: str,
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


def _granule_summary_endpoint(api_key: str, package_id: str, granule_id: str) -> str:
    """Creates an endpoint for retrieving a given granule's summary"""
    return f'/packages/{package_id}/granules/{granule_id}/summary{_query_string(api_key=api_key)}'


def _granule_content_endpoint(api_key: str, package_id: str,
                              granule_id: str, content_type: str) -> str:
    """Creates an endpoint for retrieving a given granule's content
    in the format specified by the content type"""
    endpoint = f'/packages/{package_id}/granules/{granule_id}/{content_type}'
    query_string = _query_string(api_key=api_key)
    return endpoint + query_string


def _endpoint_url(endpoint) -> str:
    """Creates a URL endpoint based on the path given"""
    return util.GOVINFO_API_URL_STR + endpoint


def _query_string(**kwargs) -> str:
    """Creates a query string from given keywords"""
    return '?' + ('&'.join([key + '=' + str(val) for key, val in kwargs.items()]))


def _current_datetime() -> str:
    """Returns the current time formatted as yyyy-MM-ddThh:mm:ssZ"""
    now = datetime.datetime.now()
    return _datetime_from_parts(now.year, now.month, now.day, now.hour, now.minute, now.second)


def _datetime_from_parts(year: int, month: int, day: int,
                         hour: int = 0, minute: int = 0, second: int = 0) -> str:
    """Returns a date/time formatted as yyyy-MM-ddThh:mm:ssZ"""
    return f'{year}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}Z'


def _datetime_to_int(datetime_str: str) -> int:
    """Converts a datetime from yyyy-MM-ddThh:mm:ssZ to yyyyMMddhhmmss"""
    date, time_str = datetime_str.replace('Z', '').split('T')
    year, month, day = date.split('-')
    hour, minute, second = time_str.split(':')
    return int(year + month + day + hour + minute + second)
