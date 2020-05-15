"""Custom errors for all things bioguide-related"""
# pylint:disable=too-few-public-methods


class InvalidRangeError(Exception):
    """An error for when a Congress range can be perceived as both years or congresses"""

    def __init__(self):
        super().__init__('Ranges that begin before 1785 but end afterwards are invalid')


class InvalidPositionError(Exception):
    """Error for when an invalid position is used"""
    def __init__(self, option: str = None):
        if option:
            msg = f'{option} is not a valid position'
        else:
            msg = f'Invalid position given'
        super().__init__(msg)


class InvalidPartyError(Exception):
    """Error for when an invalid party is used"""
    def __init__(self, option: str = None):
        if option:
            msg = f'{option} is not a valid party'
        else:
            msg = f'Invalid party given'
        super().__init__(msg)


class InvalidStateError(Exception):
    """Error for when an invalid state is used"""
    def __init__(self, option: str = None):
        if option:
            msg = f'{option} is not a valid state'
        else:
            msg = f'Invalid state given'
        super().__init__(msg)


class BioguideNotLoadedError(Exception):
    """An error for when a Bioguide property is accessed before the data has been loaded."""

    def __init__(self):
        super().__init__('The .load() method must be called when setting load_immediately=False')


class InvalidBioguideError(Exception):
    """An error for attepting to overwrite existing bioguide data"""

    def __init__(self):
        super().__init__('Invalid Bioguide')
