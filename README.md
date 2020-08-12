# V

V (or quinque) is a module for downloading data on U. S. politicians. V's goal is to empower U. S. citizens by providing an easier route for accessing the information necessary to hold public officials more accountable.
This is to be accomplished by

1) utilizing public data sources to gather information about public officials, and
2) consolidating that information in a way that's easy to code around.

As programming isn't exactly a ubiquitous skill, it cannot go without saying that V should only be considered a small, but fundamental, step in the far-greater goal of creating a more politically-informed populace. There is much more work to be done to fully realize such a goal, so V merely seeks to provide the foundation for said work.

Interested? Jump to the [samples](#tutorial) below to learn how to set up V.

***

## Table of Contents

1. [Setting up V](#tutorial)

1. [Using V](#using)

    1. [Congress](#congress)

        - [.load()](#congress_load)

        - [.bioguide](#congress_bioguide)

        - [.govinfo](#congress_govinfo)

        - [.members](#congress_members)

    1. [CongressMember](#member)

        - [.load()](#member_load)

        - [.bioguide](#member_bioguide)

        - [.govinfo](#member_govinfo)

    1. [search_congress_members()](#search)

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

        - [InvalidGovInfoErro](#invalid_govinfo_err)

        - [BioguideConnectionError](#bioguide_conn_err)

1. [About V](#about)

***

## **Setting up V**<a name="tutorial"></a>

### PyPI

V isn't available on PyPI yet, but will be submitted upon the release of v1.0 (or maybe before then - we'll see). Once it is, it will take on a new name as V is already taken (and who wants a single-letter module name anyways?)

#### Sample Project Structure

``` txt
. your_project/
+-- quinque/
+-- script.py
```

#### Sample Script

``` python
# your_project/script.py

import quinque as v
import pandas as pd

current_congress = v.Congress(116)
members = current_congress.bioguide.members
members_df = pd.DataFrame(members)
print(members_df.head())
```

#### Output

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

Currently, the only public datasets supported by V are the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp) and the [govinfo API](https://www.govinfo.gov/)*. This data can be downloaded in-bulk as tabular data using the `Congress` or `Congresses` object. More granular control can be achieved by using a `CongressMember` object.

\[\*\] *govinfo examples coming soon*

### `Congress` <a name="congress"></a>

`Congress` is used to query a single congress, and takes either a year or number to determine which congress to return.

For example, the following Congress objects all return the 116<sup>th</sup> U. S. Congress:

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

When `Congress` is instantiated, it will attempt to immediately load the requested data. To prevent this, the `load_immediately` flag can be set to `False` . From there, you can use `load()` to download the data when you are ready, like so:

``` python
c = v.Congress(116, load_immediately=False)
c.load()
```

*Note: querying a transition year favors the congress that began that year (eg `Congress(2015)` will return the 114<sup>th</sup> congress, not the 113<sup>th</sup>).*

#### `.bioguide` <a name="congress_bioguide"></a>

The `bioguide` property on a `Congress` object returns Bioguide data as a `BioguideCongressRecord` object.

``` python
c = v.Congress(116)
print(c.bioguide)
```

``` cmd
{"members": [{ .. }], "congress_number": 116, "start_year": 2019, "end_year": 2021}
```

#### `.govinfo` <a name="congress_govinfo"></a>

The `govinfo` property on a `Congress` object returns GovInfo data as `GovInfoCongressRecord` object.

#### `.members` <a name="congress_members"></a>

The `members` property on a `Congress` object returns a `list` of unique `CongressMember` objects:

``` python
c = v.Congress(116)
print(c.members[0].bioguide_id)
```

``` cmd
S001165
```

[Return to top](#table-of-contents)

***

### `CongressMember` <a name="member"></a>

The `CongressMember` class exists for querying data from the perspective of members. `CongressMember` is a much faster option for when you know the specific member(s) you would like to download data for.

`CongressMember` takes a Bioguide ID as an argument, and attempts to retrieve the specified data for the member associated with the given ID.

#### `.load()` <a name="member_load"></a>

When `CongressMember` is instantiated, it will attempt to immediately load the requested data. To prevent this, the `load_immediately` flag can be set to `False` . From there, you can use `load()` to download the data when you are ready, like so:

``` python
member = v.CongressMember('P000587', load_immediately=False)
member.load()

member_name = f'{member.first_name} {member.last_name}'
assert member_name == 'Mike Pence'
```

#### `.bioguide` <a name="member_bioguide"></a>

The `bioguide` property on a `CongressMember` object returns Bioguide data as a `BioguideMemberRecord` object.

#### `.govinfo` <a name="member_govinfo"></a>

By default, `CongressMember` will load Bioguide data for the requested member. If GovInfo data is desired, a GovInfo API key can be provided as a 2<sup>nd</sup> argument.

``` python
member = v.CongressMember('K000105', GOVINFO_API_KEY)
print(member.govinfo['title'])
```

``` cmd
Senator Edward M. Kennedy, Biography
```

Due to limitations in the GovInfo API, directly retrieving data about a member is not possible. V attempts to work around these limitations by first requesting the members Bioguide data, and using the information found there to narrow down where to locate the member's data within the GovInfo API.

[Return to top](#table-of-contents)

***

### `search_congress_members(first_name: str, last_name: str, position: str, party: str, state: str, congress: int)` <a name="search"></a>

`search_congress_members()` is a function for querying members by non-unique details.

When `search_congress_members()` is called, queries will be sent as an HTTPS POST request to bioguideretro.congress.gov. The `first_name` and `last_name` parameters will match by the beginning of the string, but `position` , `party` , and `state` will expect a selection from a discrete set of options. The available options can be found within the `Party` , `Position` , and `State` classes found within the `gpo` submodule.

[Return to top](#table-of-contents)

***

### `gpo` <a name="gpo"></a>

The `gpo` submodule is used within V to perform basic tasks for retrieving data hosted by the [United States Government Publishing Office](https://www.gpo.gov/). Within the `gpo` submodule are helper classes and functions for creating more nimble scripts.

#### `get_bioguide_ids(congress_number: int)` <a name="get_bioguide_ids"></a>

Returns the bioguide IDs of a given Congress number

#### `convert_to_congress_number(number_or_year: int)` <a name="convert_to_congress_number"></a>

Takes an input value and returns the corresponding congress number. If the number given is a valid congress number, it's returned as-is. Invalid postive numbers and `None` return the current congress, and negative numbers return zero (the Continental Congress.)

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

A class for selecting a position for `search_congress_members()`

#### `Party` <a name="party"></a>

A class for selecting a party for `search_congress_members()`

#### `State` <a name="state"></a>

A class for selecting a state for `search_congress_members()`

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
import quinque as v

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

    # For each letter, load and store the associated members
    sorted_letters = sorted(list(members_by_alphabet.keys()),
                            key=lambda k: len(members_by_alphabet[k]),
                            reverse=True)

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
                print(f'[{bioguide_id}] Downloaded    ')
            except v.gpo.BioguideConnectionError:
                print(f'[{bioguide_id}] Download Failed')

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

def write_json(data, path):
    with open(path, 'w') as file:
        json.dump(data, file)

if __name__ == '__main__':
    pre_tasks()
    main()

```

[Return to top](#table-of-contents)

***

## About V <a name="about"></a>

### Why "V"?

V is this project's code name until a PyPI-friendly name is decided. The name is an allusion to [the character V](https://en.wikipedia.org/wiki/V_(character)), of V for Vendetta, based largely on the use of his image in modern U. S. politics and the rebellious air it carries. Contrary to the character's literary interpretation, the package V is passive in nature, and promotes peaceful rebellion through the reassertion of the Peoples' power, like many who have donned the Guy Fawkes mask in peaceful protest since the movie's release.

#### What's "quinque"?

It's the Latin name of the Roman numeral "V". The python package is named this way because single-letter package names are terrible. This isn't a reference to the manga/anime [Tokyo Ghoul](https://tokyoghoul.fandom.com/wiki/Quinque), though that would be much more interesting.

### Why was V created?

Thanks to the current state of technology, the average American is individually empowered more than they have ever been before. The advent of the smartphone has made information immediately available in historically unprecedented ways, providing persons with a pocket fact-checker, productivity tool, and general entertainment. The modern laptop has become the launchpad for aspiring entrepreneurs and professionals, providing a conduit for business that enables everybody from a local craftsperson seeking to sell their wares, to a suit-clad professional in the c-suite. Those crafty enough to build their own desktop harbor enough computer power to dwarf the strongest servers of the '90's. Nonetheless, an area where citizens have seen less improvements is in that of political information, which is still mostly disseminated via media outlets. While news media is more modern than ever - having moved largely to digital means of delivery - not much has changed in the way that people use it.

Due to the competitive nature of the American economy, media outlets have been forced to set themselves apart from each other by marketing themselves to certain sets of ideologies. When occurring en masse, this can cause a single issue to be fractured into wildly-divergent perspectives. In moderation, this is a good thing, as reporting on the multiple perspectives around a single issue is integral to a functional democratic society. However, the rift between these perspectives has become so great that the average person can have a very difficult time getting a handle on the facts of a common political topic. To counter the confusion created by the media, citizens will need easier access to a more objective record of happenings within the political world. Fortunately, the publishing of such information is an existing function of the U. S. legislative branch, via the [Government Publishing Office](https://www.gpo.gov/). For more than a century, this has been the primary source for data pertaining to all three branches of the U. S. Government. While both media and GPO data are available on the internet, the succint delivery of a news article is much more alluring to the average citizen than the wordiness of a [congressional bill](https://www.congress.gov/bill/116th-congress/house-bill/748). If the average citizen is going to become less reliant on modern media for poltical information, work will need to be done to bridge this gap. The goal of V is not necessarily to be the bridge over said gap, but to be the foundation on which to build the bridge.

**Plainly stated, the function of V is to enable people to more easily gather and present poltical information.** This idea is meant to be the guiding thought for defining the scope of V - that is to say that any data that enables U. S. citizens to be more politically informed can be considered an option for V. This is, without a doubt, a very broad scope. If left uncheck, this approach could turn V into a tool that does a lot of things very poorly, with no clear direction. To guide new additions to the project and prevent the project from falling into a state of over-ambitious aimlessness, all new work will be weighed against how easy it is to implement against what exists already.

### So why Python?

At the moment, V is a collection of Python-based classes that marry disparate data sources into more easily-managed objects. That doesn't mean that V is inherently Python-based, or will never take another approach. Nor does it mean that it is poised to change anytime soon. It just means that a Python library currently makes the most sense for realizing the overall goal of V, due to the popularity of Python and its ease of use. Ideally, V is to stay in perpetual development and will always be taking the form of what makes the most sense at the time.

### What can V do?

Currently, V only supports Congressional data provided by the [Government Publishing Office](https://www.gpo.gov/). Support for social media data and stocks are planned for implementation in the near future, after which, work on the components for the Executive branch will begin.

If you'd like to contribute to the project, or know of a useful data source, feel free to submit a pull request, or [email z3c0](mailto:z3c0@21337.tech).

***

[Return to top](#table-of-contents)
