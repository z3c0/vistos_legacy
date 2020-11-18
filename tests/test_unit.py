"""Unit tests for V"""
import os
import random
import datetime
import unittest
import vistos as v

from vistos.src.gpo import util, fields, option

random.seed(43)


CURRENT_CONGRESS = 116
CURRENT_YEAR = datetime.datetime.now().year
FIRST_VALID_YEAR = 1786

EXPECTED_CONGRESS_COUNTS = {105: 549, 106: 544, 107: 552, 108: 544,
                            109: 545, 110: 554, 111: 560, 112: 552,
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


class VistosUnitTests(unittest.TestCase):
    """Test cases for testing local functionality"""

    def test_text_funcs(self):
        """Validate functions for cleaning text"""
        last_name = 'McLASTNAME'
        fixed_last_name = util.Text.fix_last_name_casing(last_name)
        self.assertEqual(fixed_last_name, 'McLastname')

    def test_first_valid_year_func(self):
        """Verify the first valid year"""

        self.assertEqual(util.first_valid_year(), FIRST_VALID_YEAR)

    def test_all_congress_numbers_func(self):
        """Verify that retrieving all congress numbers works correctly"""
        all_congress_numbers = util.all_congress_numbers()

        # +1 because Contiental Congress
        expected_congress_count = CURRENT_CONGRESS + 1

        self.assertEqual(expected_congress_count, len(all_congress_numbers))

    def test_all_congress_terms_func(self):
        """Verify that retrieving all congress terms works correctly"""
        current_congress = util.get_current_congress_number()
        all_congress_terms = util.all_congress_terms()

        # +1 because Contiental Congress
        expected_congress_count = current_congress + 1
        self.assertEqual(expected_congress_count, len(all_congress_terms))

        # verify that return value is list of 2-tuples
        max_length = max([len(t) for t in all_congress_terms])
        self.assertEqual(max_length, 2)

    def test_congress_number_conversion_func(self):
        """Validate casting numbers to the expected congress number"""

        random_sample = random.sample(range(0, 2050), 500)
        for num in random_sample:
            converted_num = util.convert_to_congress_number(num)

            if num >= CURRENT_YEAR:
                self.assertEqual(converted_num, CURRENT_CONGRESS)
            elif CURRENT_YEAR >= num >= FIRST_VALID_YEAR:
                expected_num = max(util.get_congress_numbers(num))
                self.assertEqual(converted_num, expected_num)
            elif FIRST_VALID_YEAR >= num >= CURRENT_CONGRESS:
                self.assertEqual(converted_num, CURRENT_CONGRESS)
            elif CURRENT_CONGRESS >= num >= 0:
                self.assertEqual(converted_num, num)
            elif 0 >= num:
                self.assertEqual(converted_num, 0)
            else:
                err_msg = f'Unexpected scenario: {num} -> {converted_num}'
                self.fail(err_msg)

    def test_number_year_mapping(self):
        """Verify that mapping numbers to years behaves as expected"""
        for congress_num in util.all_congress_numbers():
            if util.get_current_congress_number() >= congress_num >= 1:
                current_congress_start_year = \
                    util.get_start_year(congress_num)
                current_congress_end_year = util.get_end_year(congress_num)

                prior_congress_end_year = \
                    util.get_end_year(congress_num - 1)
                next_congress_start_year = \
                    util.get_start_year(congress_num + 1)

                self.assertEqual(prior_congress_end_year,
                                 current_congress_start_year)
                self.assertEqual(next_congress_start_year,
                                 current_congress_end_year)
            elif congress_num == 0:
                self.assertEqual(util.get_start_year(congress_num), 1786)
                self.assertEqual(util.get_end_year(congress_num), 1789)

    def test_check_for_bgmap_file(self):
        """Verfiy that bnmap file exists"""
        tests_dir = os.path.dirname(__file__)
        file_relative_path = \
            '../vistos/src/gpo/index/congress/_000.congress.bgmap'
        expected_path = os.path.join(tests_dir, file_relative_path)

        file_exists = False
        try:
            with open(expected_path, 'r'):
                file_exists = True
        except FileNotFoundError:
            pass

        self.assertTrue(file_exists)

    def test_lookup_bioguide_ids(self):
        """Verify that retrieving bioguide IDs from the index
        files behave as expected"""

        for congress, count in EXPECTED_CONGRESS_COUNTS.items():
            bioguide_ids = v.gpo.lookup_bioguide_ids(congress)
            self.assertEqual(len(bioguide_ids), count)

    def test_field_classes(self):
        """Make sure that all necessary fields are present"""
        for field in EXPECTED_BG_CONGRESS_FIELDS:
            self.assertTrue(hasattr(fields.Congress, field))

        for field in EXPECTED_BG_MEMBER_FIELDS:
            self.assertTrue(hasattr(fields.Member, field))

        for field in EXPECTED_TERM_FIELDS:
            self.assertTrue(hasattr(fields.Term, field))

    def test_current_party_class(self):
        """Varify that Democrats, Republicans, and Independents are
        accounted for in the Party.Current class"""
        for field in EXPECTED_CURRENT_PARTIES:
            self.assertTrue(hasattr(option.Party.Current, field))

    def test_bioguide_input_checker_funcs(self):
        """Vaidate functions used to verify bioguide query parameters"""
        valid_positions = [getattr(option.Position, p)
                           for p in vars(option.Position)
                           if p[:2] != '__']

        valid_states = [getattr(option.State, p)
                        for p in vars(option.State)
                        if p[:2] != '__']

        valid_parties = [getattr(option.Party.Current, p)
                         for p in vars(option.Party.Current)
                         if p[:2] != '__']

        for pos in valid_positions:
            self.assertTrue(option.is_valid_bioguide_position(pos))

        for party in valid_parties:
            self.assertTrue(option.is_valid_bioguide_party(party))

        for state in valid_states:
            self.assertTrue(option.is_valid_bioguide_state(state))

        self.assertFalse(option.is_valid_bioguide_position('123456'))
        self.assertFalse(option.is_valid_bioguide_state('123456'))
        self.assertFalse(option.is_valid_bioguide_party('123456'))


if __name__ == '__main__':
    unittest.main()
