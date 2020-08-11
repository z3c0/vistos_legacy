"""Module for interfacing with public datasets
provided by the United States Government Publishing Office"""
from quinque.src.gpo import bioguideretro as bioguide, govinfo

from quinque.src.gpo.util import CongressNumberYearMap
from quinque.src.gpo.index import get_bioguide_ids

from quinque.src.gpo.error \
    import (InvalidBioguideError,
            InvalidGovInfoError,
            BioguideConnectionError)

__all__ = ['bioguide',
           'govinfo',
           'CongressNumberYearMap',
           'get_bioguide_ids',
           'InvalidBioguideError',
           'InvalidGovInfoError',
           'BioguideConnectionError']
