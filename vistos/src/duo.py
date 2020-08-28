"""Legislative"""

import vistos.src.gpo as gpo


def search_bioguide_members(first_name=None, last_name=None, position=None,
                            party=None, state=None, congress=None):
    """queries the Bioguide for a list congress members based on the given
    search criteria"""
    bg_args = (first_name, last_name, position, party, state, congress)
    member_bioguides = gpo.bioguide.create_bioguide_members_func(*bg_args)()

    members_list = list()
    for bioguide in member_bioguides:
        member = CongressMember(bioguide.bioguide_id, load_immediately=False)
        member.bioguide = bioguide
        members_list.append(member)

    return members_list


def search_govinfo_members(govinfo_api_key, first_name=None, last_name=None,
                           position=None, party=None, state=None,
                           congress=None):
    """queries the GovInfo API for a list of congress members based on the
    given search criteria"""

    bg_args = (first_name, last_name, position, party, state, congress)
    member_bioguides = gpo.bioguide.create_bioguide_members_func(*bg_args)()

    members_list = list()
    for bioguide in member_bioguides:
        member = CongressMember(bioguide.bioguide_id, govinfo_api_key,
                                load_immediately=False)
        member.bioguide = bioguide
        member.update()
        members_list.append(member)

    return members_list


class CongressMember:
    """An object for querying data for a single Congress member"""

    def __init__(self, bioguide_id, govinfo_api_key=None,
                 load_immediately=True):
        self._bg = None
        self._gi = None

        self._bg_id = None

        self._load_member_bg = None
        self._load_member_gi = None

        self.complete_govinfo = True

        if bioguide_id is not None:
            self._bg_id = str(bioguide_id).upper()
            self._enable_bioguide()

        if govinfo_api_key is not None:
            self._enable_govinfo(govinfo_api_key)

        if load_immediately:
            self.load()

    def __str__(self):
        if self._bg_id is None:
            bioguide_id = 'Unknown'
        else:
            bioguide_id = self._bg_id

        return f'CongressMember<{bioguide_id}>'

    def load(self):
        """Load both Bioguide and GovInfo data for the member"""
        self._load_bioguide()
        self._load_govinfo()

    def update(self):
        """Loads any datasets that have not been loaded"""
        if not self._bg:
            self._load_bioguide()

        if not self._gi and self._bg:
            self._load_govinfo()

    def _load_bioguide(self):
        """Load member Bioguide data"""
        if self._load_member_bg is not None:
            self._bg = self._load_member_bg()

    def _load_govinfo(self):
        """Load member GovInfo data"""
        if self._bg is not None and self._load_member_gi is not None:
            self._gi = self._load_member_gi(self._bg)

    def _enable_bioguide(self):
        """Enable loading Bioguide data"""
        if self._bg_id is not None:
            self._load_member_bg = \
                gpo.bioguide.create_bioguide_member_func(self._bg_id)

    def _enable_govinfo(self, api_key):
        """Enable loading GovInfo data"""
        self._load_member_gi = \
            gpo.govinfo.create_member_cdir_func(api_key)

    @property
    def bioguide(self):
        """returns Bioguide data as a `BioguideMemberRecord`"""
        bioguide = None
        if hasattr(self, '_bg'):
            bioguide = self._bg
        return bioguide

    @property
    def govinfo(self):
        """returns GovInfo data as a `dict`"""
        govinfo = None
        if hasattr(self, '_gi'):
            govinfo = self._gi
        return govinfo

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = bool(new_bioguide.bioguide_id
                              and new_bioguide.first_name
                              and new_bioguide.last_name
                              and new_bioguide.terms)

        if valid_bioguide:
            self._bg = new_bioguide
            self._bg_id = new_bioguide.bioguide_id
        else:
            raise gpo.InvalidBioguideError()

    @govinfo.setter
    def govinfo(self, new_govinfo):
        try:
            _ = new_govinfo['members']
            _ = new_govinfo['members'][0]
        except (KeyError, IndexError):
            raise gpo.InvalidGovInfoError()

        try:
            _ = new_govinfo['members'][0]['bioGuideId']
        except KeyError:
            self.complete_govinfo = False

        self._gi = new_govinfo

    @property
    def bioguide_id(self):
        """The Bioguide ID of the Congress member"""
        bioguide_id = None
        if hasattr(self, '_bg_id'):
            bioguide_id = self._bg_id
        return bioguide_id

    @property
    def first_name(self):
        """returns the selected Congress member's first name"""
        first_name = None
        if hasattr(self, '_bg') and self._bg is not None:
            first_name = self._bg.first_name
        return first_name

    @property
    def nickname(self):
        """returns the selected Congress member's nickname"""
        nickname = None
        if hasattr(self, '_bg') and self._bg is not None:
            nickname = self._bg.nickname
        return nickname

    @property
    def last_name(self):
        """returns the selected Congress member's last name"""
        last_name = None
        if hasattr(self, '_bg') and self._bg is not None:
            last_name = self._bg.last_name
        return last_name

    @property
    def suffix(self):
        """returns the suffix of the selected Congress member's name"""
        suffix = None
        if hasattr(self, '_bg') and self._bg is not None:
            suffix = self._bg.suffix
        return suffix

    @property
    def birth_year(self):
        """returns the year that the selected Congress member was born"""
        birth_year = None
        if hasattr(self, '_bg') and self._bg is not None:
            birth_year = self._bg.birth_year
        return birth_year

    @property
    def death_year(self):
        """returns the year that the selected Congress member died"""
        death_year = None
        if hasattr(self, '_bg') and self._bg is not None:
            death_year = self._bg.death_year
        return death_year

    @property
    def biography(self):
        """returns biographical information about the selected Congress member
        """
        biography = None
        if hasattr(self, '_bg') and self._bg is not None:
            biography = self._bg.biography
        return biography

    @property
    def terms(self):
        """returns a `list` of `BioguideTermRecord` objects describing all of
        the terms the selected Congress member served"""
        terms = None
        if hasattr(self, '_bg') and self._bg is not None:
            terms = self._bg.terms
        return terms


class Congress:
    """An object for downloading a single Congress"""

    def __init__(self, number_or_year=None, govinfo_api_key=None,
                 include_bioguide=False, load_immediately=True):
        self._gi = None
        self._bg = None

        self._load_bg = None
        self._load_gi = None

        self._number = gpo.convert_to_congress_number(number_or_year)
        self._years = gpo.get_congress_years(self._number)

        if govinfo_api_key is not None:
            self._enable_govinfo(govinfo_api_key)

        if include_bioguide or govinfo_api_key is None:
            self._enable_bioguide()

        if load_immediately:
            self.load()

    def __str__(self):
        return f'Congress<{self.number}>'

    def load(self):
        """Manually load datasets specified when instantiating `Congress`"""
        if self._load_gi is not None:
            self._gi = self._load_gi()

        if self._load_bg is not None:
            self._bg = self._load_bg()

    def _enable_govinfo(self, key):
        """Enable loading govinfo when load() is called"""
        if self.number is not None:
            self._load_gi = gpo.govinfo.create_cdir_func(key, self.number)

    def _enable_bioguide(self):
        """Enable loading bioguide when load() is called"""
        if self.number is not None:
            self._load_bg = gpo.bioguide.create_bioguide_func(self.number)

    def get_member_bioguide(self, bioguide_id):
        """returns a `BioguideMemberRecord` corresponding to the given
        Bioguide ID"""
        if hasattr(self, '_bg') and self._bg is not None:
            for member in self._bg.members:
                if member.bioguide_id == bioguide_id:
                    return member
        return None

    def get_member_govinfo(self, bioguide_id):
        """returns a `dict` containing the GovInfo data corresponding to the
        given Bioguide ID"""
        if hasattr(self, '_gi') and self._gi is not None:
            for member in self._gi.members:
                if member['members'][0]['bioGuideId'] == bioguide_id:
                    return member
        return None

    @property
    def number(self):
        """an `int` corresponding to the number of the selected Congress"""
        number = None
        if hasattr(self, '_number'):
            number = self._number
        return number

    @property
    def start_year(self):
        """returns an `int` corresponding to the first year of the selected
        Congress"""
        start_year = None
        if hasattr(self, '_years') and len(self._years) > 0:
            start_year = self._years[0]
        return start_year

    @property
    def end_year(self):
        """returns an `int` corresponding to the first year of the selected
        Congress"""
        end_year = None
        if hasattr(self, '_years') and len(self._years) > 1:
            end_year = self._years[1]
        return end_year

    @property
    def bioguide(self):
        """returns Bioguide data as a `BioguideCongressRecord`"""
        bioguide = None
        if hasattr(self, '_bg'):
            bioguide = self._bg
        return bioguide

    @property
    def govinfo(self):
        """returns GovInfo data as `GovInfoCongressRecord`"""
        return self._gi

    @bioguide.setter
    def bioguide(self, new_bioguide):
        valid_bioguide = (new_bioguide.number is not None
                          and new_bioguide.start_year is not None
                          and new_bioguide.end_year is not None
                          and new_bioguide.members is not None)

        if valid_bioguide:
            self._bg = new_bioguide
        else:
            raise gpo.InvalidBioguideError()

    @govinfo.setter
    def govinfo(self, new_govinfo):
        valid_govinfo = (new_govinfo.number is not None
                         and new_govinfo.start_year is not None
                         and new_govinfo.end_year is not None
                         and new_govinfo.members is not None)

        if valid_govinfo:
            self._gi = new_govinfo
        else:
            raise gpo.InvalidGovInfoError()

    @property
    def members(self):
        """returns a `list` of unique `CongressMember` objects"""
        member_list = list()

        if self._bg:
            for member_record in self._bg.members:
                bioguide_id = member_record.bioguide_id
                member = CongressMember(bioguide_id, load_immediately=False)
                member.bioguide = member_record
                member_list.append(member)

        if self._gi and self._bg:
            for member_record in self._gi.members:
                try:
                    _ = (member_record['members']
                         and member_record['members'][0]
                         and member_record['members'][0]['bioGuideId'])
                except (KeyError, IndexError):
                    member = CongressMember(None, load_immediately=False)
                    member.govinfo = member_record
                    member_list.append(member)
                    continue

                bioguide_id = member_record['members'][0]['bioGuideId']
                for member in member_list:
                    if member.bioguide_id != bioguide_id:
                        continue

                    member.govinfo = member_record
        elif self._gi:
            for member_record in self._gi.members:
                try:
                    bioguide_id = member_record['members'][0]['bioGuideId']
                except (KeyError, IndexError):
                    bioguide_id = None

                member = CongressMember(bioguide_id, load_immediately=False)
                member.govinfo = member_record
                member_list.append(member)

        return member_list
