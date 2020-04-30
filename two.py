"""Legislative"""

import gpo


def get_congress_members(first_name, last_name):
    """queries for a list congress members based on name"""
    member_bioguides = gpo.get_members_func(first_name, last_name)()

    members_list = list()
    for bioguide in member_bioguides:
        member = CongressMember(bioguide.bioguide_id, False)
        member.bioguide = bioguide
        members_list.append(member)

    return members_list


class CongressMember:
    """"An object for querying data for a single Congress member"""

    def __init__(self, bioguide_id, load_immediately=True):
        self._load_member_bioguide = gpo.get_member_func(bioguide_id)

        if load_immediately:
            self.load()

    def __str__(self):
        return f'CongressMember<{self.bioguide_id}>'

    def load(self):
        """Load member dataset"""
        self._bioguide = self._load_member_bioguide()

    @property
    def bioguide(self):
        """Returns a dictionary-like object containing the \
        Bioguide information of the Congress member"""
        if self._bioguide:
            return self._bioguide
        raise BioguideNotLoadedError()

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = new_bioguide.number \
            and new_bioguide.start_year \
            and new_bioguide.end_year \
            and new_bioguide.members

        if valid_bioguide:
            self._bioguide = new_bioguide
        else:
            raise InvalidBioguideError()

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
        return self._bioguide.terms


class Congress:
    """An object for downloading a single Congress"""

    def __init__(self, number_or_year=None, load_immediately=True):
        self._load_bioguide = \
            gpo.get_single_bioguide_func(number_or_year)

        if load_immediately:
            self.load()

    def __str__(self):
        return f'Congress<{self._bioguide.number}>'

    def load(self):
        """Load specified datasets"""
        self._bioguide = self._load_bioguide()

    @property
    def bioguide(self):
        """Bioguide data for the specified Congress"""
        if self._bioguide:
            return self._bioguide
        raise BioguideNotLoadedError()

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = new_bioguide.number \
            and new_bioguide.start_year \
            and new_bioguide.end_year \
            and new_bioguide.members

        if valid_bioguide:
            self._bioguide = new_bioguide
        else:
            raise InvalidBioguideError()

    @property
    def members(self):
        """A list of members belonging to the current congress"""
        member_list = list()
        for member_record in self.bioguide.members:
            member = CongressMember(
                member_record.bioguide_id, load_immediately=False)
            member.bioguide = member_record
            member_list.append(member)

        return member_list


class Congresses:
    """An object for loading multiple Congresses into one dataset"""

    def __init__(self, start=1, end=None, load_immediately=True):
        self._load_bioguides = gpo.get_bioguides_range_func(start, end)

        if load_immediately:
            self.load()

    def __str__(self):
        numbers = set(b for b in self.bioguides)
        return f'Congresses<{min(numbers)}:{max(numbers)}>'

    def load(self):
        """Load specified datasets"""
        self._bioguides = self._load_bioguides()

    def to_list(self):
        """Returns a the Congresses data as a list of Congress objects"""
        congress_list = list()
        for bioguide in self._bioguides:
            congress = Congress(bioguide.number, False)

            # manually set the bioguide, instead of using .load()
            congress.bioguide = bioguide
            congress_list.append(congress)

        return congress_list

    @property
    def bioguides(self):
        """Bioguide data for the specified Congresses"""
        if self._bioguides:
            return self._bioguides
        raise BioguideNotLoadedError()

    @property
    def members(self):
        """A list of CongressMembers. Does not work with raw Bioguides"""
        return gpo.merge_bioguides(self.bioguides)


class BioguideNotLoadedError(Exception):
    """An error for when a Bioguide property is accessed before the data has been loaded."""

    def __init__(self):
        super().__init__('The .load() method must be called when setting load_immediately=False')


class InvalidBioguideError(Exception):
    """An error for attepting to overwrite existing bioguide data"""

    def __init__(self):
        super().__init__('Invalid Bioguide')
