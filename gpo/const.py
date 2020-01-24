"""A module for storing and manipulating constants"""
# pylint:disable=too-few-public-methods

import enum
import datetime
from typing import Set, Tuple, List, Optional


class Bioguide:
    """Constants for the GPO Bioguide"""
    # TODO: Destroy these
    BIOGUIDE_URL_STR = 'http://bioguide.congress.gov/biosearch/biosearch1.asp'
    BIOGUIDERETRO_SEARCH_URL_STR = 'https://bioguideretro.congress.gov/Home/SearchResults'
    BIOGUIDERETRO_ROOT_URL_STR = 'https://bioguideretro.congress.gov/'
    BIOGUIDERETRO_MEMBER_XML_URL = 'https://bioguideretro.congress.gov/Static_Files/data/'
    FIRST_VALID_YEAR = 1785 # no longer valid, is now 1786

    @DeprecationWarning
    class Extras(enum.Enum):
        """Enumerator for the extended bioguide content"""
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

    class CongressNumberYearMap(dict):
        def __init__(self):
            super().__init__(_NUMBER_YEAR_MAPPING)

        def get_congress_numbers(self, year: int) -> Set:
            congress_numbers = set()
            for number, years in self.items():
                if years[1] >= year >= years[0]:
                    congress_numbers.add(number)

            return congress_numbers

        def get_congress_years(self, number: int) -> Tuple:
            return self[number]

        def get_start_year(self, number: int) -> int:
            return self[number][0]

        def get_end_year(self, number: int) -> int:
            return self[number][1]

        def get_year_range_by_year(self, year: int) -> Optional[Tuple[int, int]]:
            for years in self.values():
                if years[1] >= year >= years[0]:
                    return years

        @property
        def first_valid_year(self) -> int:
            return self[0][0]

        @property
        def all_congress_numbers(self) -> List[int]:
            return list(self.keys())

        @property
        def all_congress_terms(self) -> List[Tuple[int, int]]:
            return list(self.values())

        @property
        def current_congress(self) -> int:
            """...or congresses"""
            import datetime

            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().month
            current_day = datetime.datetime.now().day

            congresses = self.get_congress_numbers(current_year)

            if current_month == 1 and current_day < 3:
                return min(congresses)

            return max(congresses)
            

    class CongressFields:
        NUMBER = 'congress_number'
        START_YEAR = 'start_year'
        END_YEAR = 'end_year'
        MEMBERS = 'members'

    class MemberFields:
        ID = 'bioguide_id'
        FIRST_NAME = 'first_name'
        MIDDLE_NAME = 'middle_name'
        LAST_NAME = 'last_name'
        NICKNAME = 'nickname'
        SUFFIX = 'suffix'
        BIRTH_YEAR = 'birth_year'
        DEATH_YEAR = 'death_year'
        BIOGRAPHY = 'biography'
        TERMS = 'terms'

    class TermFields:
        CONGRESS_NUMBER = 'congress_number'
        TERM_START = 'term_start'
        TERM_END = 'term_end'
        POSITION = 'position'
        STATE = 'state'
        PARTY = 'party'

    @DeprecationWarning
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

    @DeprecationWarning
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

    @DeprecationWarning
    class ResourceColumns:
        """Maps names to bioguide resource data.
        Changing these values changes the outputted column names.
        """
        ID = 'bioguide_id'
        PRIM_INSTITUTION = 'primary_institution'
        SEC_INSTITUTION = 'secondary_insitution' # Great, a typo -_-
        LOCATION = 'location'
        CATEGORY = 'category'
        SUMMARY = 'summary'
        DETAILS = 'details'

    @DeprecationWarning
    class BiographyColumns:
        """Maps name to bioguide biography data.
        Changing this value changes the outputted column name.
        """
        ID = 'bioguide_id'
        BIOGRAPHY = 'biography'

    @DeprecationWarning
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


_NUMBER_YEAR_MAPPING = {
    0: (1786, 1789), # Continental Congress
    1: (1789, 1791),
    2: (1791, 1793),
    3: (1793, 1795),
    4: (1795, 1797),
    5: (1797, 1799),
    6: (1799, 1801),
    7: (1801, 1803),
    8: (1803, 1805),
    9: (1805, 1807),
    10: (1807, 1809),
    11: (1809, 1811),
    12: (1811, 1813),
    13: (1813, 1815),
    14: (1815, 1817),
    15: (1817, 1819),
    16: (1819, 1821),
    17: (1821, 1823),
    18: (1823, 1825),
    19: (1825, 1827),
    20: (1827, 1829),
    21: (1829, 1831),
    22: (1831, 1833),
    23: (1833, 1835),
    24: (1835, 1837),
    25: (1837, 1839),
    26: (1839, 1841),
    27: (1841, 1843),
    28: (1843, 1845),
    29: (1845, 1847),
    30: (1847, 1849),
    31: (1849, 1851),
    32: (1851, 1853),
    33: (1853, 1855),
    34: (1855, 1857),
    35: (1857, 1859),
    36: (1859, 1861),
    37: (1861, 1863),
    38: (1863, 1865),
    39: (1865, 1867),
    40: (1867, 1869),
    41: (1869, 1871),
    42: (1871, 1873),
    43: (1873, 1875),
    44: (1875, 1877),
    45: (1877, 1879),
    46: (1879, 1881),
    47: (1881, 1883),
    48: (1883, 1885),
    49: (1885, 1887),
    50: (1887, 1889),
    51: (1889, 1891),
    52: (1891, 1893),
    53: (1893, 1895),
    54: (1895, 1897),
    55: (1897, 1899),
    56: (1899, 1901),
    57: (1901, 1903),
    58: (1903, 1905),
    59: (1905, 1907),
    60: (1907, 1909),
    61: (1909, 1911),
    62: (1911, 1913),
    63: (1913, 1915),
    64: (1915, 1917),
    65: (1917, 1919),
    66: (1919, 1921),
    67: (1921, 1923),
    68: (1923, 1925),
    69: (1925, 1927),
    70: (1927, 1929),
    71: (1929, 1931),
    72: (1931, 1933),
    73: (1933, 1935),
    74: (1935, 1937),
    75: (1937, 1939),
    76: (1939, 1941),
    77: (1941, 1943),
    78: (1943, 1945),
    79: (1945, 1947),
    80: (1947, 1949),
    81: (1949, 1951),
    82: (1951, 1953),
    83: (1953, 1955),
    84: (1955, 1957),
    85: (1957, 1959),
    86: (1959, 1961),
    87: (1961, 1963),
    88: (1963, 1965),
    89: (1965, 1967),
    90: (1967, 1969),
    91: (1969, 1971),
    92: (1971, 1973),
    93: (1973, 1975),
    94: (1975, 1977),
    95: (1977, 1979),
    96: (1979, 1981),
    97: (1981, 1983),
    98: (1983, 1985),
    99: (1985, 1987),
    100: (1987, 1989),
    101: (1989, 1991),
    102: (1991, 1993),
    103: (1993, 1995),
    104: (1995, 1997),
    105: (1997, 1999),
    106: (1999, 2001),
    107: (2001, 2003),
    108: (2003, 2005),
    109: (2005, 2007),
    110: (2007, 2009),
    111: (2009, 2011),
    112: (2011, 2013),
    113: (2013, 2015),
    114: (2015, 2017),
    115: (2017, 2019),
    116: (2019, 2021),
    117: (2021, 2023),
    118: (2023, 2025),
    119: (2025, 2027),
    120: (2027, 2029),
    121: (2029, 2031),
    122: (2031, 2033),
    123: (2033, 2035),
    124: (2035, 2037),
    125: (2037, 2039),
    126: (2039, 2041),
    127: (2041, 2043),
    128: (2043, 2045),
    129: (2045, 2047),
    130: (2047, 2049),
    131: (2049, 2051),
    132: (2051, 2053),
    133: (2053, 2055),
    134: (2055, 2057),
    135: (2057, 2059),
    136: (2059, 2061),
    137: (2061, 2063),
    138: (2063, 2065),
    139: (2065, 2067),
    140: (2067, 2069),
    141: (2069, 2071),
    142: (2071, 2073),
    143: (2073, 2075),
    144: (2075, 2077),
    145: (2077, 2079),
    146: (2079, 2081),
    147: (2081, 2083),
    148: (2083, 2085),
    149: (2085, 2087),
    150: (2087, 2089)
}
