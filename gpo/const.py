import enum

BIOGUIDE_URL_STR = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'

# Format Strings should be ONLY used with str.format()
BIOGRAPHY_URL_FORMAT_STR = 'http://bioguide.congress.gov/scripts/biodisplay.pl?index={0}'
RESOURCES_URL_FORMAT_STR = 'http://bioguide.congress.gov/scripts/guidedisplay.pl?index={0}'
BIBLIOGRAPHY_URL_FORMAT_STR = 'http://bioguide.congress.gov/scripts/bibdisplay.pl?index={0}'


class BioguideRegex:
    """Regular Expressions for cleaning bioguide data"""
    # regex101.com
    BIOGUIDE_ID = r'http:\/\/bioguide\.congress\.gov\/scripts\/biodisplay\.pl\?index=(?P<bioguide_id>[A-Z][0-9]{6})'
    NAME = r'^(?P<last>[\w\.\'\- ]+),(?: \(.+\))? (?P<first>(?:[A-Z][a-z]+|[A-Z]\.?)(?:[\-\'][A-Z][a-z]+)?)(?: (?P<middle>(?:[A-Z]\.|[A-Z][a-z]+)(?:[ -]?[A-Z][a-z]+)?))?'
    NAME_SUFFIX = r'(?: (?P<suffix>(I{1,3}|IV|V|VI{1,3}|Jr\.|Sr\.))(?: |$))'
    NAME_NICKNAME = r'\((?P<nickname>.+)\)'
    LIFESPAN = r'(?P<birth>\d{4}(?:\/\d{4})?)?\D?-\D?(?P<death>\d{4})?'
    TERM = r'(?P<congress>[0-9]{1,3})(?:\((?P<term_start>[0-9]{4})-(?P<term_end>[0-9]{4})\))?'

class BioguideRawColumns:
    """Maps names to raw bioguide data
    Changing these values changes the outputted column names
    """
    ID = 'bioguide_id'
    NAME = 'member_name'
    BIRTH_DEATH = 'birth_death'
    POSTION = 'position'
    PARTY = 'party'
    STATE = 'state'
    CONGRESS = 'congress_year'


class BioguideCleanColumns:
    """Maps names to clean bioguide data
    Changing these values changes the outputted column names
    """
    ID = 'bioguide_id'
    FIRST_NAME = 'first_name'
    MIDDLE_NAME = 'middle_name'
    LAST_NAME = 'last_name'
    NICKNAME = 'nickname'
    SUFFIX = 'suffix'
    BIRTH_YEAR = 'birth_year'
    DEATH_YEAR = 'death_year'
    POSTION = 'position'
    PARTY = 'party'
    STATE = 'state'
    CONGRESS = 'congress'
    TERM_START = 'term_start'
    TERM_END = 'term_end'
