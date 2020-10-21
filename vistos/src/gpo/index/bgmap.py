"""A module for storing bioguide data locally to speed up query times"""
import os

import vistos.src.gpo.util as util

ALL_CONGRESS_BGMAP_PATH = \
    os.path.dirname(os.path.realpath(__file__)) + '/all.congress.bgmap'


def exists_in_bgmap(congress_number: int):
    """Returns True if a given congress number exists in all.congress.bgmap"""
    current_congress = util.get_current_congress_number()
    bgmap_offset = current_congress - congress_number

    with open(ALL_CONGRESS_BGMAP_PATH, 'r') as file:
        for offset, _ in enumerate(file):
            if offset == bgmap_offset:
                return True
    return False


def get_bioguide_ids(congress_number: int = None):
    """Returns the bioguide IDs of a given Congress number"""
    current_congress = util.get_current_congress_number()

    if congress_number is not None:
        bgmap_offset = current_congress - congress_number

        bgmap = str()
        with open(ALL_CONGRESS_BGMAP_PATH, 'r') as file:
            for offset, line in enumerate(file):
                if offset == bgmap_offset:
                    bgmap = line
                    break

        return [bgmap[i:i + 7] for i in range(0, len(bgmap) - 1, 7)]
    else:
        all_bioguide_ids = set()

        for congress in range(0, current_congress + 1):
            bg_ids = get_bioguide_ids(congress)
            all_bioguide_ids = all_bioguide_ids.union(bg_ids)

        return list(all_bioguide_ids)

