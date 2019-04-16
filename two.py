"""Legislative"""
from . import gpo


class Congresses:
    """An object for loading multiple Congresses into one dataset"""

    def __init__(self, start=1, end=None, load_immediately=True, raw_bioguide=False):
        self.__load_bioguides = gpo.get_loader_func(
            start, end, True, raw_bioguide)

        if load_immediately:
            self.load()

    def load(self):
        """Load specified datasets"""
        self.__bioguide = self.__load_bioguides()

    @property
    def bioguide(self):
        """Bioguide data for the specified Congresses"""
        return self.__bioguide


class Congress:
    """An object for loading a single Congress into a dataset"""

    def __init__(self, number_or_year, load_immediately=True, raw_bioguide=False):
        self.__load_bioguide = \
            gpo.get_loader_func(start=number_or_year, load_raw=raw_bioguide)

        if load_immediately:
            self.load()

    def load(self):
        """Load specified datasets"""
        self.__bioguide = self.__load_bioguide()

    @property
    def bioguide(self):
        """Bioguide data for the specified Congress"""
        return self.__bioguide
