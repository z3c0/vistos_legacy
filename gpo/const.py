
ROOT = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'

class Regex:
    # regex101.com
    BIOGUIDE_ID = r'http:\/\/bioguide\.congress\.gov\/scripts\/biodisplay\.pl\?index=(?P<bioguide_id>[A-Z][0-9]{6})'
    NAME = r'^(?P<last>[\w\.\'\- ]+),(?: \(.+\))? (?P<first>(?:[A-Z][a-z]+|[A-Z]\.?)(?:[\-\'][A-Z][a-z]+)?)(?: (?P<middle>(?:[A-Z]\.|[A-Z][a-z]+)(?:[ -]?[A-Z][a-z]+)?))?'
    NAME_SUFFIX = r'(?: (?P<suffix>(I{1,3}|IV|V|VI{1,3}|Jr\.|Sr\.))(?: |$))'
    NAME_NICKNAME = r'\((?P<nickname>.+)\)'
    LIFESPAN = r'(?P<birth>\d{4}(?:\/\d{4})?)?\D?-\D?(?P<death>\d{4})?'
    TERM = r'(?P<congress>[0-9]{1,3})(?:\((?P<term_start>[0-9]{4})-(?P<term_end>[0-9]{4})\))?'

class RecordColumns:
    ID = 'bioguide_id'
    NAME = 'member_name'
    BIRTH_DEATH = 'birth_death'
    POSTION = 'position'
    PARTY = 'party'
    STATE = 'state'
    CONGRESS = 'congress_year'
