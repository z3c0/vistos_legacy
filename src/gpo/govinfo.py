"""A module for querying Gov Info data provided by the US GPO"""
import datetime
import json
import math

from typing import Optional, List, Callable

import requests

from five.src.gpo import util


def create_govinfo_cdir_func(api_key: str, congress: int) -> Callable[[], List[dict]]:
    """Returns a preseeded function for loading a specified congressional directory"""
    def govinfo_cdir_func() -> List[dict]:
        return _get_congressional_directory(api_key, congress)

    return govinfo_cdir_func


def check_if_congress_cdir_exists(api_key: str, congress: int) -> bool:
    """Returns true if a cdir package is available for the given congress"""
    packages = _packages_by_congress(api_key, 'CDIR', congress)
    return packages['count'] > 0



def _get_congressional_directory(api_key: str, congress: int) -> List[dict]:
    """Returns the congressional directory for the given congress number"""
    # what we're getting
    target_class = 'CONGRESSMEMBERSTATE'
    target_sub_classes = \
        {'SENATOR', 'REPRESENTATIVE', 'DELEGATE', 'RESIDENTCOMMISSIONER'}

    # actually getting it
    packages = _packages_by_congress(api_key, 'CDIR', congress)
    most_recent_package = \
        max(packages, key=lambda package: package['dateIssued'])

    package_id = most_recent_package['packageId']
    granules = _granules(api_key, package_id)

    granule_summaries = []
    for granule in granules:
        if granule['granuleClass'] == target_class:
            endpoint = _granule_summary_endpoint(
                api_key, package_id, granule['granuleId'])
            granule_text = _get_text_from(endpoint)
            granule_summary = json.loads(granule_text)
            if granule_summary.get('subGranuleClass') in target_sub_classes:
                granule_summaries.append(granule_summary)

    return granule_summaries


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

        # TODO: handle datasets larger than 10000
        if offset == 10000:
            break

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

        # TODO: handle datasets larger than 10000
        if offset == 10000:
            break

    return packages


def _collections(api_key: str) -> List[dict]:
    """Returns a list of collections"""
    collections_text = _get_text_from(_collections_endpoint(api_key))
    collections_container = json.loads(collections_text)
    return collections_container['collections']


##################################### Generic API Functions ########################################


def _get_text_from(endpoint: str) -> str:
    """Uses an HTTP GET request to retrieve text from a given endpoint"""
    response = requests.get(_endpoint_url(endpoint))
    return response.text


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
                    'offset': offset, 'pageSize': page_size}

    if congress:
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
    query_string = _query_string(
        api_key=api_key, offset=offset, pageSize=page_size)
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
    date, time = datetime_str.replace('Z', '').split('T')
    year, month, day = date.split('-')
    hour, minute, second = time.split(':')
    return int(year + month + day + hour + minute + second)
