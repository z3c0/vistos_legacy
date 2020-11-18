"""A module for storing bioguide data locally to speed up query times"""
import os

import vistos.src.gpo.util as util

ALL_CONGRESS_BGMAP_PATH = \
    os.path.dirname(os.path.realpath(__file__)) + '/all.congress.bgmap'

CONGRESS_BGMAP_PATH = (os.path.dirname(os.path.realpath(__file__))
                       + '/congress/')


# def congress_is_indexed(congress_number: int):
#    """Returns True if a given congress number exists in all.congress.bgmap"""
#     current_congress = util.get_current_congress_number()
#     bgmap_offset = current_congress - congress_number

#     with open(ALL_CONGRESS_BGMAP_PATH, 'r') as file:
#         for offset, _ in enumerate(file):
#             if offset == bgmap_offset:
#                 return True
#     return False


def exists_in_congress_index(congress_number: int):
    """Returns True if a given congress number exists in the congress bgmap
    files"""

    for _, _, file_names in os.walk(CONGRESS_BGMAP_PATH):
        for name in file_names:
            try:
                num = name.split('.')[0]
                num = num.replace('_', '')
                if int(num) == congress_number:
                    return True

            except (IndexError, ValueError, TypeError):
                continue

    return False


def lookup_bioguide_ids(congress_number: int = None):
    """Returns the bioguide IDs of a given Congress number"""
    bioguide_ids = []
    if congress_number is not None:
        for path, _, file_names in os.walk(CONGRESS_BGMAP_PATH):
            for name in file_names:
                try:
                    num = name.split('.')[0]
                    num = num.replace('_', '')
                    if int(num) == congress_number:
                        with open(path + '/' + name) as bgmap:
                            lines = bgmap.readlines()
                            bioguide_ids = [ln.replace('\n', '')
                                            for ln in lines]

                except (IndexError, ValueError, TypeError):
                    continue
    else:
        all_bioguide_ids = set()
        current_congress = util.get_current_congress_number()
        for congress in range(0, current_congress + 1):
            bg_ids = lookup_bioguide_ids(congress)
            all_bioguide_ids = all_bioguide_ids.union(bg_ids)

        return list(all_bioguide_ids)

    return bioguide_ids
