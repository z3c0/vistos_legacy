import setuptools


with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

NAME = 'quinque'
DESCRIPTION = 'A package for downloading data about U.S. politicians'
VERSION = '0.9.7'
LISCENCE = 'GPL-3.0'
AUTHOR = 'z3c0'
AUTHOR_EMAIL = 'z3c0@21337.tech'
PYTHON_VERSION = '>=3.8'
GITHUB_URL = 'https://github.com/z3c0/quinque'

KEYWORDS = \
    ['politics', 'united', 'states', 'congress', 'legislative',
     'senate', 'house', 'representatives', 'senator', 'representative',
     'delegate', 'resident', 'commissioner', 'speaker', 'government',
     'publishing', 'office']
REQUIREMENTS = \
    ['requests', 'beautifulsoup4']
CLASSIFIERS = \
    ['Development Status :: 4 - Beta',
     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
     'Intended Audience :: Developers',
     'Intended Audience :: Science/Research',
     'Programming Language :: Python :: 3.8',
     'Topic :: Sociology :: History',
     'Topic :: Education',
     'Topic :: Other/Nonlisted Topic']

setup_kwargs = {'name': NAME,
                'author': AUTHOR,
                'author_email': AUTHOR_EMAIL,
                'packages': setuptools.find_packages(),
                'include_package_data': True,
                'version': VERSION,
                'license': LISCENCE,
                'description': DESCRIPTION,
                'long_description': long_description,
                'long_description_content_type': 'text/markdown',
                'url': GITHUB_URL,
                'keywords': KEYWORDS,
                'classifiers': CLASSIFIERS,
                'python_requires': PYTHON_VERSION}

setuptools.setup(**setup_kwargs)
