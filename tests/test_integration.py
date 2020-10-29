"""Integration tests for V"""

import unittest
import vistos as v

from decouple import config


class VistosIntegrationTests(unittest.TestCase):
    """End-to-end test cases"""

    CURRENT_CONGRESS = 116
    GOVINFO_API_KEY = config('GOVINFO_API_KEY')

    def test_querying_members_by_name(self):
        """Validate congress members queried by name"""
        members = \
            v.search_bioguide_members(first_name='johnny', last_name='isakson')
        self.assertEqual(len(members), 1)

    def test_querying_members_by_position(self):
        """Validate congress members queried by position"""
        target_position = v.gpo.Position.RESIDENT_COMMISSIONER
        resident_commissioners = \
            v.search_bioguide_members(position=target_position)

        self.assertEqual(len(resident_commissioners), 33)

    def test_querying_member_by_bioguide_id(self):
        """Validate congress member queried by bioguide ID"""
        member = v.CongressMember('p000612')
        self.assertEqual(member.bioguide_id, 'P000612')

    def test_querying_member_govinfo(self):
        """Validate that requesting GovInfo for a member works"""
        members = v.search_govinfo_members(self.GOVINFO_API_KEY,
                                           last_name='butterfield')

        self.assertGreaterEqual(len(members), 2)

        govinfo = None
        for member in members:
            if member.bioguide_id == 'B001199':
                self.assertIsNone(member.govinfo)

            if member.bioguide_id == 'B001251':
                govinfo = member.govinfo

        self.assertIsNotNone(govinfo)
        self.assertEqual(govinfo['collectionCode'], 'CDIR')
        self.assertEqual(govinfo['year'], '2014')

        # Ol' Bill here was only a senator for 9 months, and died a month
        # after leaving office. He didn't serve a full term and died before
        # the term he was a part of completed. I only found out about him
        # because he broke the search_govinfo_members function.
        # No point to this story - I just thought it was interesting
        #           --z3c0
        members = v.search_govinfo_members(self.GOVINFO_API_KEY,
                                           first_name='William Stanley',
                                           last_name='West',
                                           congress=63,
                                           position='Senator',
                                           state='GA')

        self.assertEqual(len(members), 1)

    def test_congress_member(self):
        """Validate the CongressMember object"""
        member = v.CongressMember('P000587')
        member_name = f'{member.first_name} {member.last_name}'
        self.assertEqual(member_name, 'Mike Pence')

        member = v.CongressMember('K000105')
        member_name = f'{member.nickname} {member.last_name}'
        self.assertEqual(member_name, 'Ted Kennedy')
        self.assertEqual(member.first_name, 'Edward Moore')

        member = v.CongressMember('B001251')
        member_name = f'{member.nickname} {member.last_name}'
        self.assertEqual(member_name, 'G. K. Butterfield')

        member = v.CongressMember('J000120')
        full_name = f'{member.first_name} {member.last_name}, {member.suffix}'
        self.assertEqual(full_name, 'Clete Donald Johnson, Jr.')

    def test_congress_bioguide_query(self):
        """Validate retrieving Bioguide data via a Congress object"""
        congress = v.Congress(105)

        self.assertEqual(congress.number, 105)
        self.assertEqual(congress.bioguide.number, 105)

    def test_parameterless_congress_query(self):
        """Validate that exlcuding parameters from the Congress object
        results in a query for the current congress"""

        congress_a = v.Congress()
        congress_b = v.Congress(self.CURRENT_CONGRESS)

        self.assertEqual(congress_a.number, congress_b.number)
        self.assertEqual(congress_a.start_year, congress_b.start_year)
        self.assertEqual(congress_a.end_year, congress_b.end_year)
        self.assertEqual(congress_a.bioguide, congress_b.bioguide)

    def test_govinfo_congress_query(self):
        """Validate requesting govinfo data with a Congress object"""

        congress = v.Congress(115, self.GOVINFO_API_KEY)

        self.assertEqual(congress.number, 115)
        self.assertIsNotNone(congress.govinfo)

    def test_continental_congress(self):
        """Validate requests for Continental Congress data"""
        cont_congress = v.Congress(0, self.GOVINFO_API_KEY)

        self.assertEqual(cont_congress.number, 0)
        self.assertEqual(cont_congress.start_year, 1786)
        self.assertEqual(cont_congress.end_year, 1789)
        self.assertEqual(len(cont_congress.members), 366)

        self.assertIsNotNone(cont_congress.bioguide)
        self.assertIsNone(cont_congress.govinfo)

    def test_first_congress(self):
        """Validate requests for data on the first Congress"""
        congress = v.Congress(1)

        self.assertEqual(congress.number, 1)
        self.assertEqual(congress.start_year, 1789)
        self.assertEqual(congress.end_year, 1791)
        self.assertEqual(len(congress.members), 95)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNone(congress.govinfo)

    def test_1925_congress(self):
        """Validate the congress active in 1925, for no particular reason"""
        congress = v.Congress(1925)

        self.assertEqual(congress.number, 69)
        self.assertEqual(congress.start_year, 1925)
        self.assertEqual(congress.end_year, 1927)
        self.assertEqual(len(congress.members), 554)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNone(congress.govinfo)

    def test_1988_congress(self):
        """Validate the congress active in 1988"""
        congress = v.Congress(1988)
        self.assertEqual(congress.number, 100)
        self.assertEqual(congress.start_year, 1987)
        self.assertEqual(congress.end_year, 1989)
        self.assertEqual(len(congress.members), 549)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNone(congress.govinfo)

    def test_2001_congress(self):
        """Validate the congress active in 2001"""
        congress = v.Congress(2001, self.GOVINFO_API_KEY, True)

        self.assertEqual(congress.number, 107)
        self.assertEqual(congress.start_year, 2001)
        self.assertEqual(congress.end_year, 2003)
        self.assertEqual(len(congress.members), 558)
        self.assertEqual(len(congress.bioguide.members), 552)
        self.assertEqual(len(congress.govinfo.members), 533)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNotNone(congress.govinfo)

    def test_dual_dataset(self):
        """Validate requests for both Bioguide and GovInfo data"""
        congress = \
            v.Congress(115, self.GOVINFO_API_KEY, include_bioguide=True)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNotNone(congress.govinfo)

    def test_bioguide_query_object(self):
        """Validate BioguideRetroQuery"""
        query = v.gpo.bioguide.BioguideRetroQuery('wren', 'thomas')

        self.assertEqual(query.last_name, 'wren')
        self.assertEqual(query.first_name, 'thomas')

    def test_congress_bills(self):
        congress = v.Congress(105, self.GOVINFO_API_KEY)
        congress.load_bills()
        self.assertIsNotNone(congress.bills)
        self.assertEqual(len(congress.bills), 13126)


if __name__ == '__main__':
    VistosIntegrationTests.GOVINFO_API_KEY = config('GOVINFO_API_KEY')
    unittest.main()
