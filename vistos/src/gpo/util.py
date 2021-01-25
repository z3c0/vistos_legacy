"""tools for performing standard bioguide tasks"""

import datetime as _dt
import re as _re
import multiprocessing as _mp
from typing import Set, Tuple, List, Optional


BIOGUIDERETRO_SEARCH_URL_STR = \
    'https://bioguideretro.congress.gov/Home/SearchResults'
BIOGUIDERETRO_ROOT_URL_STR = \
    'https://bioguideretro.congress.gov/'
BIOGUIDERETRO_MEMBER_XML_URL = \
    'https://bioguideretro.congress.gov/Static_Files/data/'

GOVINFO_API_URL_STR = 'https://api.govinfo.gov'

MAX_REQUEST_ATTEMPTS = 3
NUMBER_OF_THREADS = _mp.cpu_count()


def first_valid_year() -> int:
    """Returns the first available year"""
    return _NUMBER_YEAR_MAPPING[0][0]


def all_congress_numbers() -> List[int]:
    """Returns all congress numbers"""
    current_congress = get_current_congress_number()
    return [num for num in _NUMBER_YEAR_MAPPING.keys()
            if current_congress >= num]


def all_congress_terms() -> List[Tuple[int, int]]:
    """Returns all two-year terms as a list
    of tuples of the start and end years"""
    current_congress = get_current_congress_number()
    return [years for num, years in _NUMBER_YEAR_MAPPING.items()
            if current_congress >= num]


def get_current_congress_number() -> int:
    """Returns the number of the active
    congress, based on the current date"""
    current_year = _dt.datetime.now().year
    current_month = _dt.datetime.now().month
    current_day = _dt.datetime.now().day

    congresses = get_congress_numbers(current_year)

    if current_month == 1 and current_day < 3:
        return min(congresses)

    return max(congresses)


def is_valid_number(number: int) -> bool:
    """Returns True if the given number is a valid Congress number"""
    return number in _NUMBER_YEAR_MAPPING.keys()


def convert_to_congress_number(number_or_year: Optional[int]) -> int:
    """Takes an input value and returns the corresponding congress number.
    If the number given is a valid congress number, it's returned as-is.
    Invalid postive numbers return the current congress, and negative
    numbers return zero (the Continental Congress.)
    """

    if number_or_year is None:
        return get_current_congress_number()

    if number_or_year >= _dt.datetime.now().year:
        return get_current_congress_number()

    if number_or_year >= first_valid_year():
        return max(get_congress_numbers(number_or_year))

    current_congress = get_current_congress_number()
    if number_or_year > current_congress:
        return current_congress

    if number_or_year >= 0:
        return number_or_year

    return 0


def get_congress_numbers(year: int) -> Set:
    """Returns the congress numbers associated with a given year"""
    congress_numbers = set()
    for number, years in _NUMBER_YEAR_MAPPING.items():
        if years[1] >= year >= years[0]:
            congress_numbers.add(number)

    return congress_numbers


def get_congress_years(number: int) -> Tuple:
    """Returns a tuple containing the start and
    end years of the given congress number"""
    return _NUMBER_YEAR_MAPPING[number]


def get_start_year(number: int) -> int:
    """Returns the start year of the given congress number"""
    return _NUMBER_YEAR_MAPPING[number][0]


def get_end_year(number: int) -> int:
    """Returns the end year of the given congress number"""
    return _NUMBER_YEAR_MAPPING[number][1]


def get_year_range_by_year(year: int) -> Optional[Tuple[int, int]]:
    """Returns the start and end years of the
    term to which the given year belongs"""
    # iterate in reverse to get most recent term
    for years in list(_NUMBER_YEAR_MAPPING.values())[::-1]:
        if years[1] >= year >= years[0]:
            return years


class Text:
    """Class for handling textual operations for the GPO module"""
    @staticmethod
    def clean_xml(text: str):
        """Removes invalid characters from XML"""
        # negation of valid characters
        invalid_char = r'[^a-zA-Z0-9\s~`!@#$%^&*()_+=:{}[;<,>.?/\\\-\]\"\']'
        clean_text = _re.sub(invalid_char, '', text)
        return clean_text

    @staticmethod
    def fix_last_name_casing(name: str) -> str:
        """Converts uppercase text to capitalized"""
        # Addresses name prefixes, like "Mc-" or "La-"
        if _re.match(r'^[A-Z][a-z][A-Z]', name):
            start_pos = 3
        else:
            start_pos = 1

        capital_case = name[:start_pos] + name[start_pos:].lower()
        return capital_case


_NUMBER_YEAR_MAPPING = {
    0: (1786, 1789),  # Continental Congress
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
