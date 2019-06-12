"""A module for storing and manipulating constants"""
# pylint:disable=too-few-public-methods

import enum


class Bioguide:
    """Constants for the GPO Bioguide"""
    BIOGUIDE_URL_STR = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'
    FIRST_VALID_YEAR = 1785

    class Extras(enum.Enum):
        """Enumerator for the extra content"""
        BIOGRAPHY = 'http://bioguide.congress.gov/scripts/biodisplay.pl'
        RESOURCES = 'http://bioguide.congress.gov/scripts/guidedisplay.pl'
        BIBLIOGRAPHY = 'http://bioguide.congress.gov/scripts/bibdisplay.pl'

    class Regex:
        """Regular Expressions for cleaning bioguide data"""
        BIOGUIDE_ID = r'http:\/\/bioguide\.congress\.gov\/scripts\/biodisplay\.pl' + \
            r'\?index=(?P<bioguide_id>[A-Z][0-9]{6})'
        NAME = r'^(?P<last>[\w\.\'\- ]+),(?: \(.+\))? ' + \
            r'(?P<first>(?:[A-Z][a-z]+|[A-Z]\.?)(?:[\-\'][A-Z][a-z]+)?)' + \
            r'(?: (?P<middle>(?:[A-Z]\.|[A-Z][a-z]+)(?:[ -]?[A-Z][a-z]+)?))?'
        NAME_SUFFIX = r'(?: (?P<suffix>(I{1,3}|IV|V|VI{1,3}|Jr\.|Sr\.))(?: |$))'
        NAME_NICKNAME = r'\((?P<nickname>.+)\)'
        LIFESPAN = r'(?P<birth>\d{4}(?:\/\d{4})?)?\D?-\D?(?P<death>\d{4})?'
        TERM = r'(?P<congress>[0-9]{1,3})(?:\((?P<term_start>[0-9]{4})-(?P<term_end>[0-9]{4})\))?'

    class RawColumns:
        """Maps names to raw bioguide data.
        Changing these values changes the outputted column names.
        """
        ID = 'bioguide_id'
        NAME = 'member_name'
        BIRTH_DEATH = 'birth_death'
        POSTION = 'position'
        PARTY = 'party'
        STATE = 'state'
        CONGRESS = 'congress_year'

    class CleanColumns:
        """Maps names to clean bioguide data.
        Changing these values changes the outputted column names.
        """
        ID = 'bioguide_id'
        FIRST_NAME = 'first_name'
        MIDDLE_NAME = 'middle_name'
        LAST_NAME = 'last_name'
        NICKNAME = 'nickname'
        SUFFIX = 'suffix'
        BIRTH_YEAR = 'birth_year'
        DEATH_YEAR = 'death_year'
        POSITION = 'position'
        PARTY = 'party'
        STATE = 'state'
        CONGRESS = 'congress'
        TERM_START = 'term_start'
        TERM_END = 'term_end'

    class ResourceColumns:
        """Maps names to bioguide resource data.
        Changing these values changes the outputted column names.
        """
        ID = 'bioguide_id'
        PRIM_INSTITUTION = 'primary_institution'
        SEC_INSTITUTION = 'secondary_insitution'
        LOCATION = 'location'
        CATEGORY = 'category'
        SUMMARY = 'summary'
        DETAILS = 'details'

    class BiographyColumns:
        """Maps name to bioguide biography data.
        Changing this value changes the outputted column name.
        """
        ID = 'bioguide_id'
        BIOGRAPHY = 'biography'

    class BibliographyColumns:
        """Maps name to bioguide biography data.
        Changing this value changes the outputted column name.
        """
        ID = 'bioguide_id'
        CITATION = 'citation'

    class InvalidRangeError(Exception):
        """An error for when a Congress range can be perceived as both years or congresses"""
        def __init__(self):
            super().__init__('Ranges that begin before 1785 but end afterwards are invalid')
