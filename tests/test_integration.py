"""Integration tests for V"""

import os
import unittest
import quinque as v
import quinque_test as v_test


class QuinqueIntegrationTests(unittest.TestCase):
    """End-to-end test cases"""

    GOVINFO_API_KEY = os.environ.get('GOVINFO_API_KEY', None)

    def test_congress_bioguide_query(self):
        """Validate retrieving Bioguide data via a Congress object"""
        congress = v.Congress(105)

        self.assertEqual(congress.number, 105)
        self.assertEqual(congress.bioguide.number, 105)

    def test_parameterless_congress_query(self):
        """Validate that exlcuding parameters from the Congress object
        results in a query for the current congress"""

        congress_a = v.Congress()
        congress_b = v.Congress(v_test.CURRENT_CONGRESS)

        self.assertEqual(congress_a.number, congress_b.number)
        self.assertEqual(congress_a.start_year, congress_b.start_year)
        self.assertEqual(congress_a.end_year, congress_b.end_year)
        self.assertEqual(congress_a.bioguide, congress_b.bioguide)

    def test_govinfo_congress_query(self):
        """Validate requesting govinfo data with a Congress object"""

        congress = v.Congress(115, self.GOVINFO_API_KEY)

        self.assertEqual(congress.number, 115)
        self.assertIsNotNone(congress.govinfo)


if __name__ == '__main__':
    QuinqueIntegrationTests.GOVINFO_API_KEY = os.environ['GOVINFO_API_KEY']
    unittest.main()
