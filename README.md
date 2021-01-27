# Vistos

## (v1.0.8+) !!! GovInfo API functionality is currently disabled !!!
### Due to recent changes in the GovInfo API, the Vistos GovInfo API components have become very unstable. Until a fix can be devised, the govinfo attributes on the Congress and CongressMember classes will be disabled.

***

Vistos is a module for downloading data on U. S. politicians from public sources via HTTP. V's goal is to empower U. S. citizens by providing an easier route for accessing the information necessary to hold public officials more accountable.
This is to be accomplished by

1) utilizing public data sources to gather information about public officials, and
2) consolidating that information in a way that's easy to code around.

As programming isn't exactly a ubiquitous skill, it cannot go without saying that Vistos should only be considered a small, but fundamental, step in the far-greater goal of creating a more politically-informed populace. There is much more work to be done to fully realize such a goal, so Vistos merely seeks to provide the foundation for said work.

Interested? Jump to the [samples](#tutorial) below to learn how to set up Vistos.

***

## Table of Contents

1. [Setting up Vistos](#tutorial)

1. [Using Vistos](#using)

    1. [CongressMember](#member)

        - [.load()](#member_load)

        - [.bioguide](#member_bioguide)

        - [.govinfo](#member_govinfo)

        - [.bioguide_id](#member_bioguide_id)

        - [.first_name](#member_first_name)

        - [.nickname](#member_nickname)

        - [.last_name](#member_last_name)

        - [.suffix](#member_suffix)

        - [.birth_year](#member_birth_year)

        - [.death_year](#member_death_year)

        - [.biography](#member_biography)

        - [.terms](#member_terms)

    1. [Congress](#congress)

        - [.load()](#congress_load)

        - [.get_member_bioguide()](#get_member_bioguide)

        - [.get_member_govinfo()](#get_member_govinfo)

        - [.number](#congress_number)

        - [.start_year](#congress_start_year)

        - [.end_year](#congress_end_year)

        - [.bioguide](#congress_bioguide)

        - [.govinfo](#congress_govinfo)

        - [.members](#congress_members)
    
    1. [CongressBills](#congress_bills)

        - [.load()](#congress_bills_load)

    1. [search_bioguide_members()](#search-bg)

    1. [search_govinfo_members()](#search-gi)

    1. [gpo](#gpo)

        - [get_bioguide_ids()](#get_bioguide_ids)

        - [convert_to_congress_number()](#convert_to_congress_number)

        - [get_start_year()](#get_start_year)

        - [get_end_year()](#get_end_year)

        - [get_congress_years()](#get_congress_years)

        - [get_congress_numbers()](#get_congress_numbers)

        - [all_congress_numbers()](#all_congress_numbers)

        - [Position](#position)

        - [Party](#party)

        - [State](#state)

        - [InvalidBioguideError](#invalid_bioguide_err)

        - [InvalidGovInfoError](#invalid_govinfo_err)

        - [BioguideConnectionError](#bioguide_conn_err)

1. [About Vistos](#about)

1. [Known Issues and Workarounds](#issues)

***

## **Setting up V**<a name="tutorial"></a>

``` cmd
pip install vistos
```

### Sample Script

``` python
# your_project/script.py

import vistos as v
import pandas as pd

current_congress = v.Congress(116)
members = current_congress.bioguide.members
members_df = pd.DataFrame(members)
print(members_df.head())
```

### Output

``` cmd
>> python ~/your_project/script.py
  bioguide_id              first_name ... terms
0     S001165                   Albio ... [{'congress_number': 109, 'term_start': 2005, ...
1     R000603                   David ... [{'congress_number': 114, 'term_start': 2015, ...
2     S001172                  Adrian ... [{'congress_number': 110, 'term_start': 2007, ...
3     C001049            William Lacy ... [{'congress_number': 107, 'term_start': 2001, ...
4     H001076           Margaret Wood ... [{'congress_number': 115, 'term_start': 2017, ...
```

[Return to top](#table-of-contents)

***

## **Using V** <a name="using"></a>

Currently, the only public datasets supported by Vistos are the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp) and the [GovInfo API](https://www.govinfo.gov/). This data can be downloaded in-bulk as tabular data using the `Congress` object. More granular control can be achieved by using a `CongressMember` object.

To use the GovInfo API, an API key is required. You can sign up for one [here](https://api.data.gov/signup/).

***

### `CongressMember` <a name="member"></a>

The `CongressMember` class exists for querying data from the perspective of members. `CongressMember` is a much faster option for when you know the specific member(s) you would like to download data for.

`CongressMember` takes a Bioguide ID as an argument, and attempts to retrieve data for the member associated with the given ID.

#### `.load()` <a name="member_load"></a>

The `load` method manually loads the datasets specified when instantiating `CongressMember`

``` python
member = v.CongressMember('P000587', load_immediately=False)
member.load()

member_name = f'{member.first_name} {member.last_name}'
assert member_name == 'Mike Pence'
```

#### `.bioguide` <a name="member_bioguide"></a>

The `bioguide` property returns Bioguide data as a `BioguideMemberRecord` .

#### `.govinfo` <a name="member_govinfo"></a>

The `govinfo` property returns GovInfo data as a `dict` .

``` python
member = v.CongressMember('K000105', GOVINFO_API_KEY)
print(member.govinfo['title'])
```

Output:

``` cmd
Senator Edward M. Kennedy, Biography
```

Due to limitations in the GovInfo API, directly retrieving data about a member is not possible. Vistos attempts to work around these limitations by first requesting the members Bioguide data, and using the information found there to narrow down where to locate the member's data within the Congressional Directories of the Congresses the member belonged to.

#### `.bioguide_id` <a name="member_bioguide_id"></a>

The `bioguide_id` property returns the selected Congress member's Bioguide ID.

#### `.first_name` <a name="member_first_name"></a>

The `first_name` property returns the selected Congress member's first name.

#### `.nickname` <a name="member_nickname"></a>

The `nickname` property returns the selected Congress member's nickname.

#### `.last_name` <a name="member_last_name"></a>

The `last_name` property returns the selected Congress member's last name.

#### `.suffix` <a name="member_suffix"></a>

The `suffix` property returns the suffix of the selected Congress member's name.

#### `.birth_year` <a name="member_birth_year"></a>

The `birth_year` property returns the year that the selected Congress member was born.

#### `.death_year` <a name="member_death_year"></a>

The `death_year` property returns the year that the selected Congress member died.

#### `.biography` <a name="member_biography"></a>

The `biography` property returns biographical information about the selected Congress member.

#### `.terms` <a name="member_terms"></a>

The `terms` property returns a `list` of `BioguideTermRecord` objects describing all of the terms the selected Congress member served.

[Return to top](#table-of-contents)

***

### `Congress` <a name="congress"></a>

`Congress` is used to query a single congress, and takes either a year or number to determine which congress to return.

For example, the following `Congress` objects all return the 116<sup>th</sup> U. S. Congress:

``` python
a = v.Congress(116)
b = v.Congress(2019)
c = v.Congress(2020)
assert a.bioguide == b.bioguide == c.bioguide
```

Excluding a year or number will return the active U. S. Congress:

``` python
c = v.Congress()
assert c.number == 116
```

#### `.load()` <a name="congress_load"></a>

Manually load datasets specified when instantiating `Congress`

``` python
c = v.Congress(116, load_immediately=False)
c.load()
```

*Note: querying a transition year favors the congress that began that year (eg `Congress(2015)` will return the 114<sup>th</sup> congress, not the 113<sup>th</sup>).*

#### `.get_member_bioguide(bioguide_id: str)` <a name="get_member_bioguide"></a>

Calling `get_member_bioguide()` returns a `BioguideMemberRecord` corresponding to the given Bioguide ID.

#### `.get_member_govinfo(bioguide_id: str)` <a name="get_member_govinfo"></a>

Calling `get_member_govinfo()` returns a `dict` containing the GovInfo data corresponding to the given Bioguide ID.

#### `.number` <a name="congress_number"></a>

The `number` property returns an `int` corresponding to the number of the selected Congress.

#### `.start_year` <a name="congress_start_year"></a>

The `start_year` property returns an `int` corresponding to the first year of the selected Congress.

#### `.end_year` <a name="congress_end_year"></a>

The `end_year` property returns an `int` corresponding to the last year of the selected Congress.

#### `.bioguide` <a name="congress_bioguide"></a>

The `bioguide` property returns Bioguide data as a `BioguideCongressRecord` .

``` python
c = v.Congress(116)
print(c.bioguide)
```

Output:

``` cmd
{"members": [{ .. }], "congress_number": 116, "start_year": 2019, "end_year": 2021}
```

#### `.govinfo` <a name="congress_govinfo"></a>

The `govinfo` property returns GovInfo data as a `GovInfoCongressRecord` .

#### `.members` <a name="congress_members"></a>

The `members` property returns a `list` of unique `CongressMember` objects:

``` python
c = v.Congress(116)
print(c.members[0].bioguide_id)
```

Output:

``` cmd
S001165
```

[Return to top](#table-of-contents)

***
### `CongressBills` <a name="congress_bills"></a>

`CongressBills` is a `list`-based object for querying the bills for a single congress. This is in contrast to the `Congress` object, which will attempt to download member data first.

``` python
congress_bills = v.CongressBills(105)
print(len(congress_bills))
```

Output:

``` cmd
13126
```
#### `.load()` <a name="congress_bills_load"></a>

The `load` method manually loads the dataset specified when instantiating `CongressBills`

[Return to top](#table-of-contents)

***

### `search_bioguide_members(first_name: str, last_name: str, position: str, party: str, state: str, congress: int)` <a name="search-bg"></a>

`search_bioguide_members()` is a function for querying members by non-unique details.

When `search_bioguide_members()` is called, queries will be sent as an HTTPS POST request to bioguideretro.congress.gov. The `first_name` and `last_name` parameters will match by the beginning of the string, but `position` , `party` , and `state` will expect a selection from a discrete set of options. The available options can be found within the `Party` , `Position` , and `State` classes found within the `gpo` submodule.

### `search_govinfo_members(govinfo_api_key: str, first_name: str, last_name: str, position: str, party: str, state: str, congress: int)` <a name="search-gi"></a>

`search_govinfo_members()` works similarly to `search_bioguide_members()` , but attempts to include GovInfo data for matching members.

[Return to top](#table-of-contents)

***

### `gpo` <a name="gpo"></a>

The `gpo` submodule is used within Vistos to perform basic tasks for retrieving data hosted by the [United States Government Publishing Office](https://www.gpo.gov/). Within the `gpo` submodule are helper classes and functions for creating more nimble scripts.

#### `get_bioguide_ids(congress_number: int)` <a name="get_bioguide_ids"></a>

Returns the bioguide IDs of a given Congress number

#### `convert_to_congress_number(number_or_year: int)` <a name="convert_to_congress_number"></a>

Takes an input value and returns the corresponding congress number. If the number given is a valid congress number, it's returned as-is. If the number given is a valid year, the corresponding congress number is returned. Invalid postive numbers and `None` return the current congress, and negative numbers return zero (the Continental Congress.)

#### `get_current_congress_number()` <a name="get_current_congress_number"></a>

Returns the number of the active congress, based on the current date

#### `get_start_year(number: int)` <a name="get_start_year"></a>

Returns the start year of the given congress number

#### `get_end_year(number: int)` <a name="get_end_year"></a>

Returns the end year of the given congress number

#### `get_congress_years(number: int)` <a name="get_congress_years"></a>

Returns a tuple containing the start and end years of the given congress number

#### `get_congress_numbers(year: int)` <a name="get_congress_numbers"></a>

Returns the congress numbers associated with a given year

#### `all_congress_numbers()` <a name="all_congress_numbers"></a>

Returns all congress numbers

#### `Position` <a name="position"></a>

A class containing options for the position parameter of `search_congress_members()`

#### `Party` <a name="party"></a>

A class containing options for the party parameter of `search_congress_members()`

#### `State` <a name="state"></a>

A class containing options for the state parameter of `search_congress_members()`

#### `InvalidBioguideError` <a name="invalid_bioguide_err"></a>

An error for when an attempt is made to assign incorrectly-shaped data to the `Congress.bioguide` or `CongressMember.bioguide` properties.

#### `InvalidGovInfoError` <a name="invalid_govinfo_err"></a>

An error for when an attempt is made to assign incorrectly-shaped data to the `Congress.govinfo` or `CongressMember.govinfo` properties.

#### `BioguideConnectionError` <a name="bioguide_conn_err"></a>

An error for when an HTTP connection error is raised during Bioguide queries. This can be used to handle instability caused by requesting large amounts of members.

[Return to top](#table-of-contents)

***

### **Examples**<a name="examples"></a>

#### `CongressMember` <a name="member-example"></a>

Below is an example of how to use the `CongressMember` object and the `gpo.get_bioguide_ids()` function to download all the members of the last ten Congresses, storing each in a JSON file per the first letter of their last name.

``` python

import os
import json
import shutil
import vistos as v

OUTPUT_DIR = './members_by_letter'
CURRENT_CONGRESS = v.gpo.get_current_congress_number()

def main():
    # This script downloads data about Congress members for the past
    # ten Congresses, using the CongressMember object in conjunction with
    # the gpo.get_bioguide_ids() function.

    # Get unique bioguides from the prior 10 years
    all_bioguide_ids = set()
    start_congress, end_congress = \
        CURRENT_CONGRESS - 10, CURRENT_CONGRESS

    for congress in range(start_congress, end_congress + 1):
        bioguide_ids = v.gpo.get_bioguide_ids(congress)
        all_bioguide_ids = all_bioguide_ids.union(bioguide_ids)

    # Map Bioguide IDs to their corresponding letter
    # of the alphabet (denoted by the first character)
    members_by_alphabet = dict()
    for bioguide_id in all_bioguide_ids:
        letter = str(bioguide_id[0]).lower()
        try:
            member = v.CongressMember(bioguide_id, load_immediately=False)
            members_by_alphabet[letter].append(member)
        except KeyError:
            members_by_alphabet[letter] = [member]

    sorted_letters = sorted(list(members_by_alphabet.keys()),
                            key=lambda k: len(members_by_alphabet[k]),
                            reverse=True)

    # For each letter, load and store the associated members
    for letter in sorted_letters:
        congress_members = members_by_alphabet.pop(letter)

        member_headers = []
        member_terms = []

        while len(congress_members) > 0:
            member = congress_members.pop(0)
            bioguide_id = member.bioguide_id

            # Download data
            print(f'[{bioguide_id}] Downloading...', end='\r')
            try:
                member.load()
                print(f'[{bioguide_id}] Downloaded    ', end='')
            except v.gpo.BioguideConnectionError:
                print(f'[{bioguide_id}] Download Failed', end='')
            finally:
                print()

            # Split terms from the rest of the data
            member_header_record = dict(member.bioguide)
            del member_header_record['terms']

            member_headers.append(member_header_record)
            member_terms.append({'bioguide_id': member.bioguide_id,
                                 'terms': member.bioguide.terms})

        # Save data
        file_name = f'{start_congress}_{end_congress}_{letter}'
        headers_path = create_path('headers', file_name)
        terms_path = create_path('terms', file_name)

        json.dump(member_headers, open(headers_path, 'w'))
        print(f'[{letter.upper()}------] Saved Member data to {headers_path}')

        json.dump(member_terms, open(terms_path, 'w'))
        print(f'[{letter.upper()}------] Saved Term data to {terms_path}')

def pre_tasks():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def create_path(category, file_name):
    if not os.path.exists(OUTPUT_DIR + '/' + category):
        os.makedirs(OUTPUT_DIR + '/' + category)

    return f'{OUTPUT_DIR}/{category}/{category}_{file_name}.json'

if __name__ == '__main__':
    pre_tasks()
    main()

```

[Return to top](#table-of-contents)

***

## About Vistos <a name="about"></a>

### Vistos' Purpose

Plainly stated, the function of Vistos is to enable people to more easily gather and present poltical information. This idea is meant to be the guiding thought for defining the scope of Vistos - that is to say that any data that enables U. S. citizens to be more politically informed can be considered an option for Vistos. To guide new additions to the project and prevent the project from falling into a state of over-ambitious aimlessness, all new work will be weighted by how easy it is to implement against what exists already.

### On the Use of Python

At the moment, Vistos is a collection of Python-based classes that marry disparate data sources into more easily-managed objects. That doesn't mean that Vistos is inherently Python-based, or will never take another approach. Nor does it mean that it is poised to change anytime soon. It just means that a Python library currently makes the most sense for realizing the overall goal of Vistos, due to the popularity of Python and its ease of use. Ideally, Vistos is to stay in perpetual development and will always be taking the form of whatever makes the most sense at the time.

### Long Term Goals

Currently, Vistos only supports Congressional data provided by the [Government Publishing Office](https://www.gpo.gov/). Support for social media data and stocks are planned for implementation in the near future, after which, work on the components for the Executive branch will begin. On a more functional level, there are plans for verbosity and CLI support.

If you'd like to contribute to the project, or know of a useful data source, feel free to submit a pull request, or [email z3c0](mailto:z3c0@21337.tech).

***

[Return to top](#table-of-contents)

## Known Issues and Workarounds <a name="issues"></a>

1. Querying GovInfo does not return results for some congress persons.

    When using the `CongressMember` class, some congress persons will not return GovInfo data. This is due to their GovInfo data missing a Bioguide ID, which is used for finding individual records within a Congressional Directory package. Should you need data for one of these members, the only workaround (currently) is to instead query GovInfo for the entire Congress that they served for, using the `Congress` class.

1. GovInfo data only goes as far back as the 105<sup>th</sup> Congress

    The GovInfo API makes congress persons' data available via "Congressional Directories", which are only provided starting with the 105<sup>th</sup> Congress. If data for an earlier congress is needed, use Bioguide data instead.
    
