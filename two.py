"""Legislative"""

import gpo


class Term:
    """The details of a Congress member's term"""

    def __init__(self, bioguide_id, term_record):
        self.bioguide_id = bioguide_id
        self.congress_number = term_record.congress_number
        self.start_year = term_record.start_year
        self.end_year = term_record.end_year
        self.position = term_record.position
        self.state = term_record.state
        self.party = term_record.party

    def __str__(self):
        return f'CongressionalTerm<{self.bioguide_id}:{self.congress_number}>'


class CongressMember:
    """"An object for querying data for a single Congress member"""

    def __init__(self, first_name, last_name, load_immediately=True, verbose=False):
        self._load_member_bioguide = gpo.get_member_bioguide_func(first_name, last_name, verbose)

        if load_immediately:
            self.load()

    def __str__(self):
        return f'CongressMember<{self.bioguide_id}>'

    def load(self):
        """Load member dataset"""
        # TODO: handle multiple members being returned from a single search
        self._bioguide = self._load_member_bioguide()[0]

    @property
    def bioguide_id(self):
        """The Bioguide ID of the Congress member"""
        return self._bioguide.bioguide_id

    @property
    def first_name(self):
        """The first name of the Congress member"""
        return self._bioguide.first_name

    @property
    def last_name(self):
        """The last name of the Congress memeber"""
        return self._bioguide.last_name

    @property
    def birth_year(self):
        """The year the Congress member was born"""
        return self._bioguide.birth_year

    @property
    def death_year(self):
        """The year the Congress member died"""
        return self._bioguide.death_year

    @property
    def biography(self):
        """The biography of the Congress member"""
        return self._bioguide.biography

    @property
    def terms(self):
        """The terms the Congress member has served"""
        return [Term(self.bioguide_id, t) for t in self._bioguide.terms]



class Congress:
    """An object for downloading a single Congress"""

    def __init__(self, number_or_year, load_immediately=True, verbose=False):
        self._load_bioguide = \
            gpo.get_bioguide_func(
                start=number_or_year, verbose=verbose)

        if load_immediately:
            self.load()

    def __str__(self):
        return f'Congress<{self._bioguide.number}>'

    def load(self):
        """Load specified datasets"""
        self._bioguide = self._load_bioguide()[0]

    @property
    def bioguide(self):
        """Bioguide data for the specified Congress"""
        if not self._bioguide:
            self.load()

        return self._bioguide

    @property
    def members(self):
        """A list of members belonging to the current congress"""
        return self._bioguide.members

    @property
    def number(self):
        """The number of the current congress"""
        return self._bioguide.number

    @property
    def start_year(self):
        """The year that the current congress began"""
        return self._bioguide.start_year

    @property
    def end_year(self):
        """The year that the current congress ended, or will end"""
        return self._bioguide.end_year


class Congresses:
    """An object for loading multiple Congresses into one dataset"""

    def __init__(self, start=1, end=None, load_immediately=True, verbose=False):
        self._load_bioguide = gpo.get_bioguide_func(
            start, end, True, verbose)

        if load_immediately:
            self.load()

    def __str__(self):
        congress_numbers = set(c.number for c in self._bioguide)
        min_congress = min(congress_numbers)
        max_congress = max(congress_numbers)
        return f'Congresses<{min_congress}:{max_congress}>'

    def load(self):
        """Load specified datasets"""
        self._bioguide = self._load_bioguide()

    @property
    def bioguide(self):
        """Bioguide data for the specified Congress"""
        if not self._bioguide:
            self.load()

        return self._bioguide

    @property
    def members(self):
        """A list of CongressMembers. Does not work with raw Bioguides"""
        return gpo.merge_bioguides(self._bioguide)



