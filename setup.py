from distutils.core import setup


PACKAGE_NAME = 'quinque'
PACKAGE_DESC = 'A package for downloading data about U.S. politicians'
PACKAGE_VERS = '0.9.3'
PACKAGE_LISC = 'GPL-3.0'

setup_kwargs = {'name': PACKAGE_NAME,
                'packages': [PACKAGE_NAME],
                'version': PACKAGE_VERS,
                'license': PACKAGE_LISC,
                'description': PACKAGE_DESC}

setup(**setup_kwargs)
