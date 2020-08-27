#!python3.8
"""vistos (V)"""
import os

from vistos.src import Congress, CongressMember, search_congress_members, gpo

__all__ = ['gpo', 'Congress', 'CongressMember', 'search_congress_members']

VERSION = open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'r').read()
