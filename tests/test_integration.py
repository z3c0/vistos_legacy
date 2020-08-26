"""Integration tests for V"""

import unittest
import quinque as v


class QuinqueIntegrationTests(unittest.TestCase):
    """End-to-end test cases"""

    def test_congress_bioguide_query(self):
        """Validate retrieving Bioguide data via a Congress object"""
        congress = v.Congress(105)
        self.assertEqual(congress.number, 105)
        self.assertEqual(congress.bioguide.number, 105)
