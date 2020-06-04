"""Legislative"""

import five.src.gpo as gpo


def search_congress_member(first_name=None, last_name=None, position=None, party=None, state=None):
    """queries for a list congress members based on name"""
    bioguide_args = (first_name, last_name, position, party, state)
    member_bioguides = gpo.create_bioguide_members_func(*bioguide_args)()

    members_list = list()
    for bioguide in member_bioguides:
        member = CongressMember(bioguide.bioguide_id, False)
        member.bioguide = bioguide
        members_list.append(member)

    return members_list


class CongressMember:
    """"An object for querying data for a single Congress member"""

    def __init__(self, bioguide_id, load_immediately=True):
        self._load_member_bioguide = \
            gpo.create_bioguide_member_func(bioguide_id)

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
        raise gpo.error.BioguideNotLoadedError()

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = new_bioguide.bioguide_id \
            and new_bioguide.first_name \
            and new_bioguide.last_name \
            and new_bioguide.terms

        if valid_bioguide:
            self._bioguide = new_bioguide
        else:
            raise gpo.error.InvalidBioguideError()

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

    def __init__(self, number_or_year=None, govinfo_api_key=None, include_bioguide=False, load_immediately=True):
        self._load_govinfo = lambda *n: None
        self._load_bioguide = lambda *n: None

        year_map = gpo.util.CongressNumberYearMap()
        self.number = year_map.convert_to_congress_number(number_or_year)

        if load_immediately:
            if govinfo_api_key:
                self.enable_govinfo_api(govinfo_api_key)

            if include_bioguide or not govinfo_api_key:
                self.enable_bioguide()

            self.load()

    def __str__(self):
        return f'Congress<{self._bioguide.number}>'

    def load(self):
        """Load specified datasets"""
        self._govinfo = self._load_govinfo()
        self._bioguide = self._load_bioguide()

    def enable_govinfo_api(self, key):
        if gpo.check_if_congress_cdir_exists(key, self.number):
            self._load_govinfo = gpo.create_govinfo_cdir_func(key, self.number)

    def enable_bioguide(self):
        self._load_bioguide = gpo.create_single_bioguide_func(self.number)

    @property
    def bioguide(self):
        """Bioguide data for the specified Congress"""
        if self._bioguide:
            return self._bioguide
        raise gpo.error.BioguideNotLoadedError()

    @property
    def govinfo(self):
        """GovInfo data for the specified Congress"""
        if self._govinfo:
            return self._govinfo
        raise gpo.error.GovInfoNotLoadedError()

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = new_bioguide.number \
            and new_bioguide.start_year \
            and new_bioguide.end_year \
            and new_bioguide.members

        if valid_bioguide:
            self._bioguide = new_bioguide
        else:
            raise gpo.error.InvalidBioguideError()

    @property
    def members(self):
        """A list of members belonging to the current congress"""
        member_list = list()
        for member_record in self.bioguide.members:
            member = CongressMember(member_record.bioguide_id, False)
            member.bioguide = member_record
            member_list.append(member)

        return member_list


class Congresses:
    """An object for loading multiple Congresses into one dataset"""

    def __init__(self, start=1, end=None, load_immediately=True, members_as_list=True):
        self._load_bioguides = gpo.create_multi_bioguides_func(start, end)

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
        raise gpo.error.BioguideNotLoadedError()

    @property
    def members(self):
        """A list of CongressMembers. Does not work with raw Bioguides"""
        member_list = list()
        for member_record in self.bioguides.members:
            member = CongressMember(member_record.bioguide_id, False)
            member.bioguide = member_record
            member_list.append(member)

        return member_list
