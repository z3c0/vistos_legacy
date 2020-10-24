#!python3.8
"""vistos (V)"""
from os import path as _path

from vistos.src import (Congress, CongressMember, search_bioguide_members,
                        search_govinfo_members, gpo)

__all__ = ['gpo', 'Congress', 'CongressMember', 'search_bioguide_members',
           'search_govinfo_members']

VERSION = open(_path.join(_path.dirname(__file__), 'VERSION'), 'r').read()
