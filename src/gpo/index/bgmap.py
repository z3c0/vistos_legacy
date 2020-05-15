"""A module for storing bioguide data locally to speed up query times"""
import os
import json
import five.src.gpo as gpo
import five.src.gpo.const.util as util

ALL_CONGRESS_BGMAP_PATH = os.path.dirname(os.path.realpath(__file__)) + '\\all.congress.bgmap'


def exists_in_bgmap(congress_number):
    """Returns True if a given congress number exists in congress.bgmap"""
    current_congress = util.CongressNumberYearMap().current_congress
    bgmap_offset = current_congress - congress_number

    with open(ALL_CONGRESS_BGMAP_PATH, 'r') as file:
        for offset, _ in enumerate(file):
            if offset == bgmap_offset:
                return True
    return False



def get_bioguide_ids(congress_number):
    """Fetch the bioguide IDs of a given Congress number"""
    current_congress = util.CongressNumberYearMap().current_congress
    bgmap_offset = current_congress - congress_number

    bgmap = str()
    with open(ALL_CONGRESS_BGMAP_PATH, 'r') as file:
        for offset, line in enumerate(file):
            if offset == bgmap_offset:
                bgmap = line
                break

    return [bgmap[i:i + 7] for i in range(0, len(bgmap) - 1, 7)]
