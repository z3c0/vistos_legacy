"""Test cases for downloading data"""
import unittest
import quinque as v


govinfo_api_key = ''  # open('./govinfo_key.txt', 'r').read()


class QueryTestCases(unittest.TestCase):

    def test_querying_members_by_name(self):
        """Validate congress members queried by name"""
        members = \
            v.search_congress_members(first_name='johnny', last_name='isakson')
        self.assertEqual(len(members), 1)

    def test_querying_members_by_position(self):
        """Validate congress members queried by position"""
        target_position = v.gpo.Position.RESIDENT_COMMISSIONER
        resident_commissioners = \
            v.search_congress_members(position=target_position)

        self.assertEqual(len(resident_commissioners), 33)

    def test_querying_member_by_bioguide_id(self):
        """Validate congress member queried by bioguide ID"""
        member = v.CongressMember('p000612')
        self.assertEqual(member.bioguide_id, 'P000612')

    def test_querying_member_govinfo(self):
        """Validate that requesting GovInfo for a member works"""
        members = v.search_congress_members(last_name='butterfield')

        self.assertGreaterEqual(len(members), 2)

        govinfo = None
        for member in members:
            member.enable_govinfo(govinfo_api_key)
            member.load_govinfo()

            if member.bioguide_id == 'B001199':
                self.assertIsNone(member.govinfo)

            if member.bioguide_id == 'B001251':
                govinfo = member.govinfo

        self.assertIsNotNone(govinfo)
        self.assertEqual(govinfo['collectionCode'], 'CDIR')
        self.assertEqual(govinfo['year'], '2014')

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

    def test_current_congress(self):
        """Validate Congress object"""
        congress = v.Congress(govinfo_api_key=govinfo_api_key)

        # check that no parameter results in
        # the current congress (116 as of 2020)
        self.assertEqual(congress.number, 116)

        # GovInfo data is historical, so the
        # current congress should return a
        # Bioguide, even when given a key
        self.assertIsNotNone(congress.bioguide)
        self.assertIsNone(congress.govinfo)

    def test_govinfo(self):
        """Validate requests for GovInfo data"""
        congress = v.Congress(115, govinfo_api_key=govinfo_api_key)

        self.assertIsNotNone(congress.govinfo)
        self.assertIsNone(congress.bioguide)

    def test_bioguide(self):
        """Validate requests for Bioguide data"""
        congress = v.Congress(115)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNone(congress.govinfo)

    def test_continental_congress(self):
        """Validate requests for Continental Congress data"""
        cont_congress = v.Congress(0, govinfo_api_key)

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
        congress = v.Congress(2001, govinfo_api_key, include_bioguide=True)

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
            v.Congress(115, govinfo_api_key, include_bioguide=True)

        self.assertIsNotNone(congress.bioguide)
        self.assertIsNotNone(congress.govinfo)

    def test_bioguide_query_object(self):
        """Validate BioguideRetroQuery"""
        query = v.gpo.bioguide.BioguideRetroQuery('wren', 'thomas')

        self.assertEqual(query.last_name, 'wren')
        self.assertEqual(query.first_name, 'thomas')


if __name__ == '__main__':
    unittest.main()
