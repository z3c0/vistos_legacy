"""Field names for gpo objects"""


class Congress:
    """Headers for BioguideCongressRecord and GovInfoCongressRecord"""
    NUMBER = 'congress_number'
    START_YEAR = 'start_year'
    END_YEAR = 'end_year'
    MEMBERS = 'members'


class Member:
    """Headers for BioguideMemberRecord"""
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


class Term:
    """Headers for BioguideTermRecord"""
    CONGRESS_NUMBER = 'congress_number'
    TERM_START = 'term_start'
    TERM_END = 'term_end'
    POSITION = 'position'
    STATE = 'state'
    PARTY = 'party'
    SPEAKER_OF_THE_HOUSE = 'house_speaker'


class Bill:
    """Headers for GovInfoBillRecord"""
    BILL_ID = 'bill_id'
    CONGRESS = 'congress_number'
    TITLE = 'title'
    SHORT_TITLE = 'short_title'
    DATE_ISSUED = 'date_issued'
    PAGES = 'pages'
    GOVERNMENT_AUTHOR = 'government_author'
    DOC_CLASS_NUMBER = 'doc_class_number'
    BILL_TYPE = 'bill_type'
    ORIGIN_CHAMBER = 'origin_chamber'
    CURRENT_CHAMBER = 'current_chamber'
    SESSION = 'session'
    BILL_NUMBER = 'bill_number'
    BILL_VERSION = 'bill_version'
    IS_APPROPRATION = 'is_appropriation'
    IS_PRIVATE = 'is_private'
    PUBLISHER = 'publisher'
    COMMITTEES = 'committees'
    MEMBERS = 'members'
