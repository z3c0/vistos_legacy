"""Legislative"""
from . import gpo


class PersonalDetails:
    """The unchanging details of the Congress member"""

    def __init__(self, **kwargs):
        self.first_name = kwargs.get('first_name')
        self.last_name = kwargs.get('last_name')
        self.middle_name = kwargs.get('middle_name')
        self.nickname = kwargs.get('nickname')
        self.suffix = kwargs.get('suffix')
        self.birth_year = kwargs.get('birth_year')
        self.death_year = kwargs.get('death_year')

    def to_dict(self):
        """Returns personal details as a dictionary"""
        return {
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'nickname': self.nickname,
            'suffix': self.suffix,
            'birth_year': self.birth_year,
            'death_year': self.death_year,
        }

    def to_list(self):
        """Returns personal details as a list"""
        return [
            self.first_name,
            self.middle_name,
            self.last_name,
            self.nickname,
            self.suffix,
            self.birth_year,
            self.death_year
        ]


class Term:
    """The details of a Congress member's term"""

    def __init__(self, **kwargs):
        self.position = kwargs.get('position')
        self.party = kwargs.get('party')
        self.state = kwargs.get('state')
        self.congress = kwargs.get('congress')
        self.start_year = kwargs.get('start_year')
        self.end_year = kwargs.get('end_year')

    def __str__(self):
        return f'CongressionalTerm<{self.start_year}, {self.end_year}>'

    def to_dict(self):
        """Returns term data as a dictionary"""
        return {
            'position': self.position,
            'party': self.party,
            'state': self.state,
            'congress': self.congress,
            'term_start': self.start_year,
            'term_end': self.end_year
        }

    def to_list(self):
        """Returns term data as a list"""
        return [
            self.position,
            self.party,
            self.state,
            self.congress,
            self.start_year,
            self.end_year
        ]


class CongressMember:
    """"An object for storing data for a single Congress member"""

    def __init__(self, **kwargs):
        is_query = 'first_name' in kwargs and 'last_name' in kwargs
        is_record = 'bioguide' in kwargs

        assert not (is_record and is_query), \
            'The arguments first_name, last_name, bioguide cannot be used simultaneously.'

        self.bioguide_id = None
        self.details = None
        self.terms = []

        if is_record:
            bioguide = kwargs.get('bioguide')
            self.bioguide_id = bioguide.bioguide_id

        elif is_query:
            first_name_search = kwargs.get('first_name')
            last_name_search = kwargs.get('last_name')
            records = gpo.get_member_bioguide(
                first_name_search, last_name_search)
            bioguide = records.pop(0)
            self.bioguide_id = bioguide.bioguide_id
            for record in records:
                _add_bioguide_record(self, record)


        birth_year = int(bioguide.birth_year)
        death_year = int(
            bioguide.death_year) if bioguide.death_year else None

        self.details = PersonalDetails(
            first_name=bioguide.first_name,
            middle_name=bioguide.middle_name,
            last_name=bioguide.last_name,
            nickname=bioguide.nickname,
            suffix=bioguide.suffix,
            birth_year=birth_year,
            death_year=death_year
        )

        self.terms = [Term(
            position=bioguide.position,
            party=bioguide.party,
            state=bioguide.state,
            congress=bioguide.congress,
            start_year=bioguide.term_start,
            end_year=bioguide.term_end
        )] + self.terms

        self.biography = None
        self.bibliography = None
        self.resources = None

    def __str__(self):
        return f'CongressMember<{self.bioguide_id}>'

    def to_records(self):
        """Returns an array of dictionaries containing the Congress member's data."""
        records = list()
        personal_details = self.details.to_dict()
        for term in self.terms:
            record = {**personal_details, **term.to_dict()}
            records.append(record)

        return records

    def load_extended_bioguide(self):
        """Load biography, bibliography, and resources data"""
        self.load_biography()
        self.load_bibliography()
        self.load_resources()

    def load_biography(self):
        """Load member's biography"""
        self.biography = gpo.get_biography(self.bioguide_id)

    def load_bibliography(self):
        """Load member's bibliography"""
        self.bibliography = gpo.get_bibliography(self.bibliography)

    def load_resources(self):
        """Load member's resources"""
        self.resources = gpo.get_resources(self.resources)


class Congress:
    """An object for loading a single Congress into a dataset"""

    def __init__(self, number_or_year, load_immediately=True, raw_bioguide=False):
        self._load_bioguide = \
            gpo.get_bioguide_func(
                start=number_or_year, load_raw=raw_bioguide)

        if load_immediately:
            self.load()

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
        if self._bioguide and 'congress' in self._bioguide[0]:
            members = {}
            for record in self._bioguide:
                try:
                    _add_bioguide_record(members[record.bioguide_id], record)
                except KeyError:
                    members[record.bioguide_id] = CongressMember(
                        bioguide=record)

        return list(members.values())


class Congresses:
    """An object for loading multiple Congresses into one dataset"""

    def __init__(self, start=1, end=None, load_immediately=True, raw_bioguide=False):
        self._load_bioguide = gpo.get_bioguide_func(
            start, end, True, raw_bioguide)

        if load_immediately:
            self.load()

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
        if self._bioguide and 'congress' in self._bioguide[0]:
            members = {}
            for record in self._bioguide:
                try:
                    _add_bioguide_record(members[record.bioguide_id], record)
                except KeyError:
                    members[record.bioguide_id] = CongressMember(
                        bioguide=record)

        return list(members.values())


def _add_bioguide_record(congress_member, record):
    """Add more Bioguide information"""
    assert record.bioguide_id == congress_member.bioguide_id, 'Bioguide IDs must match'

    try:
        member_congresses = map(
            lambda term: term.congress, congress_member.terms)
        index = list(member_congresses).index(record.congress)

        congress_member.terms[index].position = record.position
    except ValueError:
        congress_member.terms.append(Term(
            position=record.position,
            party=record.party,
            state=record.state,
            congress=record.congress,
            start_year=record.term_start,
            end_year=record.term_end
        ))
