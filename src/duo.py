"""Legislative"""

import quinque.src.gpo as gpo


def _null_function():
    return None


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

    def __init__(self, bioguide_id=None, load_immediately=True):
        self._bg = None
        self._gi = None

        self._load_member_bg = _null_function

        if bioguide_id:
            self.enable_bioguide(bioguide_id)

            if load_immediately:
                self.load()

    def __str__(self):
        return f'CongressMember<{self.bioguide_id}>'

    def load(self):
        """Load member dataset"""
        self._bg = self._load_member_bg()

    def enable_bioguide(self, bioguide_id):
        """Enable loading bioguide data"""
        self._load_member_bg = \
            gpo.create_bioguide_member_func(bioguide_id)

    @property
    def bioguide(self):
        """Returns a dictionary-like object containing the
        Bioguide data of the current Congress member"""
        return self._bg

    @property
    def govinfo(self):
        """Returns a JSON object containing the GovInfo data
        of the current Congress member"""
        return self._gi

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = bool(new_bioguide.bioguide_id
                              and new_bioguide.first_name
                              and new_bioguide.last_name
                              and new_bioguide.terms)

        if valid_bioguide:
            self._bg = new_bioguide
            self.enable_bioguide(new_bioguide.bioguide_id)
        else:
            raise gpo.InvalidBioguideError()

    @govinfo.setter
    def govinfo(self, new_govinfo):
        try:
            _ = new_govinfo['members']
            _ = new_govinfo['members'][0]
            _ = new_govinfo['members'][0]['bioGuideId']
            self._gi = new_govinfo
        except (KeyError, IndexError):
            raise gpo.InvalidGovInfoError()

    @property
    def bioguide_id(self):
        """The Bioguide ID of the Congress member"""
        bioguide_id = None

        if self._gi:
            bioguide_id = self._gi['members'][0]['bioGuideId']
        elif self._bg:
            bioguide_id = self._bg.bioguide_id

        return bioguide_id

    # @property
    # def first_name(self):
    #     """The first name of the Congress member"""
    #     return self._bg.first_name

    # @property
    # def last_name(self):
    #     """The last name of the Congress memeber"""
    #     return self._bg.last_name

    # @property
    # def birth_year(self):
    #     """The year the Congress member was born"""
    #     return self._bg.birth_year

    # @property
    # def death_year(self):
    #     """The year the Congress member died"""
    #     return self._bg.death_year

    # @property
    # def biography(self):
    #     """The biography of the Congress member"""
    #     return self._bg.biography

    # @property
    # def terms(self):
    #     """The terms the Congress member has served"""
    #     return self._bg.terms


class Congress:
    """An object for downloading a single Congress"""

    def __init__(self, number_or_year=None, govinfo_api_key=None,
                 include_bioguide=False, load_immediately=True,
                 verbose=False):

        self._verbose = verbose

        self._gi = None
        self._bg = None

        self._load_gi = _null_function
        self._load_bg = _null_function

        year_map = gpo.CongressNumberYearMap()
        self._number = year_map.convert_to_congress_number(number_or_year)
        self._years = year_map.get_congress_years(self._number)

        cdir_exists = False
        if govinfo_api_key:
            cdir_exists = \
                gpo.check_if_cdir_exists(govinfo_api_key, self.number)

        if cdir_exists:
            self.enable_govinfo_api(govinfo_api_key)

        if include_bioguide or not cdir_exists:
            self.enable_bioguide()

        if load_immediately:
            self.load()

    def __str__(self):
        return f'Congress<{self.number}>'

    def load(self):
        """Load specified datasets"""
        self._gi = self._load_gi()
        self._bg = self._load_bg()

    def enable_govinfo_api(self, key):
        """Enables loading data from the GovInfo API"""
        if self._verbose:
            self._load_gi = \
                gpo.create_verbose_govinfo_cdir_func(key, self.number)
        else:
            self._load_gi = gpo.create_govinfo_cdir_func(key, self.number)

    def enable_bioguide(self):
        """Enables loading data from the Congressional Bioguide"""
        if self._verbose:
            self._load_bg = \
                gpo.create_verbose_single_bioguide_func(self.number)
        else:
            self._load_bg = gpo.create_single_bioguide_func(self.number)

    def get_member_bioguide(self, bioguide_id):
        """Returns the bioguide data for the member corresponding
        to the given bioguide ID"""
        if self._bg:
            for member in self._bg.members:
                if member.bioguide_id == bioguide_id:
                    return member
        return None

    def get_member_govinfo(self, bioguide_id):
        """Returns the govinfo data for the member corresponding
        to the given bioguide ID"""
        if self._gi:
            for member in self._gi.members:
                if member['members'][0]['bioGuideId'] == bioguide_id:
                    return member
        return None

    @property
    def number(self):
        """The number of the given Congress"""
        return self._number

    @property
    def start_year(self):
        """The year that the given Congress began"""
        return self._years[0]

    @property
    def end_year(self):
        """The year that the given Congress ended"""
        return self._years[1]

    @property
    def bioguide(self):
        """Bioguide data for the given Congress"""
        return self._bg

    @property
    def govinfo(self):
        """GovInfo data for the given Congress"""
        return self._gi

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = new_bioguide.number and new_bioguide.start_year \
            and new_bioguide.end_year and new_bioguide.members

        if valid_bioguide:
            self._bg = new_bioguide
        else:
            raise gpo.InvalidBioguideError()

    @govinfo.setter
    def govinfo(self, new_govinfo):
        valid_govinfo = new_govinfo.number and new_govinfo.start_year \
            and new_govinfo.end_year and new_govinfo.members

        if valid_govinfo:
            self._gi = new_govinfo
        else:
            raise gpo.InvalidGovInfoError()

    @property
    def members(self):
        """A list of members belonging to the current Congress"""
        member_list = list()

        if self._gi:
            for member_record in self._gi.members:
                member = CongressMember(load_immediately=False)
                try:
                    member.govinfo = member_record
                except gpo.InvalidGovInfoError:
                    continue
                member_list.append(member)

        elif self._bg:
            for member_record in self._bg.members:
                member = CongressMember(load_immediately=False)
                try:
                    member.bioguide = member_record
                except gpo.InvalidBioguideError:
                    continue
                member_list.append(member)

        return member_list
