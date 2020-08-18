"""Test cases for V"""
import unittest
import quinque as v


govinfo_api_key = ''  # open('./govinfo_key.txt', 'r').read()


class FunctionTestCases(unittest.TestCase):
    """Test cases for testing local functionality"""

    def test_number_year_mapping(self):
        """Verify the structure of the number-to-year mapping dict"""
        for congress_num in v.gpo.all_congress_numbers():
            if v.gpo.get_current_congress_number() >= congress_num >= 1:
                current_congress_start_year = \
                    v.gpo.get_start_year(congress_num)
                current_congress_end_year = v.gpo.get_end_year(congress_num)

                prior_congress_end_year = \
                    v.gpo.get_end_year(congress_num - 1)
                next_congress_start_year = \
                    v.gpo.get_start_year(congress_num + 1)

                self.assertEqual(prior_congress_end_year,
                                 current_congress_start_year)
                self.assertEqual(next_congress_start_year,
                                 current_congress_end_year)
            elif congress_num == 0:
                self.assertEqual(v.gpo.get_start_year(congress_num), 1786)
                self.assertEqual(v.gpo.get_end_year(congress_num), 1789)

    def test_congress_year_mapping(self):
        """Verify that a querying a congress multiple
        ways results in the same object"""
        congress_a = v.Congress(1)
        congress_b = v.Congress(1789)
        congress_c = v.Congress(1790)
        self.assertEqual(congress_a.bioguide,
                         congress_b.bioguide,
                         congress_c.bioguide)

    def test_bgmap_file(self):
        """Test functions for parsing bgmap files"""
        bioguide_ids = v.gpo.get_bioguide_ids(1)

        self.assertEqual(len(bioguide_ids), 95)


if __name__ == '__main__':
    unittest.main()
