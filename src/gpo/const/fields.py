"""Field names for gpo objects"""
# pylint:disable=too-few-public-methods

class Congress:
    """Headers for BioguideCongressRecord"""
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
