"""Legislative"""
from . import gpo as gpo


class Congresses:
    def __init__(self, start=1, end=None, load_immediately=True, raw_bioguide=False):
        self.__load_bioguides = gpo.get_loader_func(start, end, True, raw_bioguide)

        if load_immediately:
            self.load()

    def load(self):
        self.bioguide = self.__load_bioguides()


class Congress:
    def __init__(self, number_or_year, load_immediately=True, raw_bioguide=False):
        self.__load_bioguide = gpo.get_loader_func(start=number_or_year, load_raw=raw_bioguide)

        if load_immediately:
            self.load()

    def load(self):
        self.bioguide = self.__load_bioguide()



class CongressMember:
    def __init__(self, last_name, first_name, position, state, year):
        pass
