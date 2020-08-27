import datetime

CURRENT_CONGRESS = 116
CURRENT_YEAR = datetime.datetime.now().year
FIRST_VALID_YEAR = 1786

EXPECTED_CONGRESS_COUNTS = {105: 549, 106: 544, 107: 552, 108: 544,
                            109: 545, 110: 554, 111: 559, 112: 552,
                            113: 554, 114: 547, 115: 561}

EXPECTED_BG_CONGRESS_FIELDS = ['NUMBER', 'START_YEAR',
                               'END_YEAR', 'MEMBERS']

EXPECTED_BG_MEMBER_FIELDS = ['ID', 'FIRST_NAME', 'MIDDLE_NAME',
                             'LAST_NAME', 'NICKNAME', 'SUFFIX',
                             'BIRTH_YEAR', 'DEATH_YEAR', 'BIOGRAPHY',
                             'TERMS']

EXPECTED_TERM_FIELDS = ['CONGRESS_NUMBER', 'TERM_START', 'TERM_END',
                        'POSITION', 'STATE', 'PARTY',
                        'SPEAKER_OF_THE_HOUSE']

EXPECTED_POSITION_FIELDS = ['REPRESENTATIVE', 'SENATOR', 'DELEGATE',
                            'VICE_PRESIDENT', 'PRESIDENT',
                            'CONTINENTAL_CONGRESS', 'SPEAKER_OF_THE_HOUSE',
                            'RESIDENT_COMMISSIONER']

EXPECTED_CURRENT_PARTIES = ['DEMOCRAT', 'INDEPENDENT', 'REPUBLICAN']
