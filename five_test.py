"""Unit tests, duh"""
import unittest

import src as v
from src.gpo.const import Bioguide as bg


class TestCongressObject(unittest.TestCase):
    """Test cases for the Congress object of the two module"""

    def test_first_congress(self):
        """Validate the first congress"""
        congress = v.Congress(1)
        self.assertEqual(congress.bioguide.number, 1)
        self.assertEqual(congress.bioguide.start_year, 1789)
        self.assertEqual(congress.bioguide.end_year, 1791)
        self.assertEqual(len(congress.members), 95)

    def test_1925_congress(self):
        """Validate the congress active in 1925, for no particular reason"""
        congress = v.Congress(1925)
        self.assertEqual(congress.bioguide.number, 69)
        self.assertEqual(congress.bioguide.start_year, 1925)
        self.assertEqual(congress.bioguide.end_year, 1927)
        self.assertEqual(len(congress.members), 554)

    def test_1988_congress(self):
        """Validate the congress active in 1988"""
        congress = v.Congress(1988)
        self.assertEqual(congress.bioguide.number, 100)
        self.assertEqual(congress.bioguide.start_year, 1987)
        self.assertEqual(congress.bioguide.end_year, 1989)
        self.assertEqual(len(congress.members), 549)

    def test_congress_year_mapping(self):
        """Verify that a querying a congress multiple ways results in the same object"""
        congress_a = v.Congress(116)
        congress_b = v.Congress(2019)
        congress_c = v.Congress(2020)
        self.assertEqual(congress_a.bioguide,
                         congress_b.bioguide, congress_c.bioguide)


class TestCongressesObject(unittest.TestCase):
    """Validate the Congresses object of the two module"""

    def test_downloading_multiple_congresses(self):
        """Validate congresses from 2015 to 2020"""
        congresses = v.Congresses(2015, 2020)
        self.assertEqual(len(congresses.members), 720)
        self.assertEqual(set(b.number for b in congresses.bioguides), {114, 115, 116})


class TestCongressMemberObject(unittest.TestCase):
    """Validate the CongressMember object of the two module"""

    def test_querying_member_by_bioguide_id(self):
        """Validate congress member queried by bioguide ID"""
        member = v.CongressMember('p000612')
        self.assertEqual(member.bioguide_id, 'P000612')
        self.assertEqual(member.last_name, 'Perdue')
        self.assertEqual(int(member.birth_year), 1949)


class TestConstants(unittest.TestCase):
    """Verify the integrity of the constants in the GPO module"""


    def test_number_year_mapping(self):
        """Verify the structure of the number-to-year mapping dict"""
        year_map = bg.CongressNumberYearMap()

        for congress_num in year_map:
            if year_map.current_congress >= congress_num >= 1:
                current_congress_start_year = year_map.get_start_year(
                    congress_num)
                current_congress_end_year = year_map.get_end_year(congress_num)

                prior_congress_end_year = year_map.get_end_year(
                    congress_num - 1)
                next_congress_start_year = year_map.get_start_year(
                    congress_num + 1)

                self.assertEqual(prior_congress_end_year,
                                 current_congress_start_year)
                self.assertEqual(next_congress_start_year,
                                 current_congress_end_year)
            elif congress_num == 0:
                self.assertEqual(year_map.get_start_year(congress_num), 1786)
                self.assertEqual(year_map.get_end_year(congress_num), 1789)


if __name__ == '__main__':
    unittest.main()
