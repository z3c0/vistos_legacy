"""Unit tests, duh"""
from two import Congress
from gpo.const import Bioguide as bg


def run_tests():
    """Put all test functions here"""
    _validate_number_year_mapping()
    _validate_congress_object()

    print('unit tests passed')


def _validate_congress_object():
    print('testing Congress object...')

    # test the 1st congress
    print('downloading the 1st Congress')
    congress = Congress(1)
    assert congress.number == 1, 'The 1st Congress number should equal 1'
    assert congress.start_year == 1789, 'The 1st Congress start year shoud equal 1789'
    assert congress.end_year == 1791, 'The 1st Congress end year shoud equal 1791'
    assert len(congress.members) == 95, 'The 1st Congress should have 95 members'

    # test the 69th congress
    print('downloading Congress 1925')
    congress = Congress(1925)
    assert congress.number == 69, '1925\'s Congress number should equal 69'
    assert congress.start_year == 1925, '1925\'s Congress start year shoud equal 1925'
    assert congress.end_year == 1927, '1925\'s Congress end year shoud equal 1927'
    assert len(congress.members) == 554, '1925\'s Congress should have 554 members'

    # test the 100th congress
    print('downloading Congress 1988')
    congress = Congress(1988)
    assert congress.number == 100, '1988\'s Congress number should equal 100'
    assert congress.start_year == 1987, '1988\'s Congress start year shoud equal 1987'
    assert congress.end_year == 1989, '1988\'s Congress end year shoud equal 1989'
    assert len(congress.members) == 549, '1988\'s Congress should have 549 members'

    # query the 116th congress in multiple ways
    print('testing the 116th Congress downloaded via number, start year, and end year')
    print('downloading Congress 116')
    congress_a = Congress(116)

    print('downloading Congress 2019')
    congress_b = Congress(2019)

    print('downloading Congress 2020')
    congress_c = Congress(2020)

    assert congress_a.bioguide == congress_b.bioguide == congress_c.bioguide, \
        ('bioguides for 116, 2019, and 2020 should match' \
            + f'\n\nCongress 116:' \
            + f'\tnumber:{congress_a.bioguide.number}' \
            + f'\tyears:{congress_a.bioguide.start_year}-{congress_a.bioguide.end_year}' \
            + f'\tmembers:{len(congress_a.bioguide.members)}' \
            + f'\n\nCongress 2019:' \
            + f'\tnumber:{congress_b.bioguide.number}' \
            + f'\tyears:{congress_b.bioguide.start_year}-{congress_b.bioguide.end_year}' \
            + f'\tmembers:{len(congress_b.bioguide.members)}' \
            + f'\n\nCongress 2020:' \
            + f'\tnumber:{congress_c.bioguide.number}' \
            + f'\tyears:{congress_c.bioguide.start_year}-{congress_c.bioguide.end_year}' \
            + f'\tmembers:{len(congress_c.bioguide.members)}')


def _validate_congresses_object():
    """Test cases for the Congresses class"""
    #TODO: Congresses test cases


def _validate_congress_member_object():
    """Test cases for the CongressMember class"""
    #TODO: CongressMember test cases


def _validate_number_year_mapping():
    """Test cases for validating the _NUMBER_YEAR_MAPPING constant"""

    print('testing _NUMBER_YEAR_MAPPING constant...')
    year_map = bg.CongressNumberYearMap()

    for congress_num in year_map:
        if year_map.current_congress >= congress_num >= 1:
            current_congress_start_year = year_map.get_start_year(congress_num)
            current_congress_end_year = year_map.get_end_year(congress_num)

            prior_congress_end_year = year_map.get_end_year(
                congress_num - 1)
            next_congress_start_year = year_map.get_start_year(
                congress_num + 1)

            assert prior_congress_end_year == current_congress_start_year, \
                f'Congress {congress_num} must have a start year ' + \
                f'equal to the end year of Congress {congress_num - 1}'
            assert next_congress_start_year == current_congress_end_year, \
                f'Congress {congress_num} must have an end year ' + \
                f'equal to the start year of Congress {congress_num + 1}'
        elif congress_num == 0:
            assert year_map.get_start_year(congress_num) == 1786
            assert year_map.get_end_year(congress_num) == 1789
