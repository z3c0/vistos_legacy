
# five

five is a module for downloading data on US politicians, with the overall goal of making political data more accessible to developers. Currently, you can import this module by placing the project in the root of your application and using a relative import.


#### Sample Project Structure
``` 
. your_project/
+-- five/
+-- script.py
```
#### Sample Script
``` python
# your_project/script.py

import five as v
import pandas as pd

current_congress = v.Congress(116)
members = current_congress.bioguide.members
members_df = pd.DataFrame(members)
print(members_df.head())
```
#### Output
```
>> python ~/your_project/script.py
  bioguide_id              first_name ... terms
0     S001165                   Albio ... [{'congress_number': 109, 'term_start': 2005, ...
1     R000603                   David ... [{'congress_number': 114, 'term_start': 2015, ...
2     S001172                  Adrian ... [{'congress_number': 110, 'term_start': 2007, ...
3     C001049       William Lacy, Jr. ... [{'congress_number': 107, 'term_start': 2001, ...
4     H001076  Margaret Wood (Maggie) ... [{'congress_number': 115, 'term_start': 2017, ...
```

***

# Using five

Currently, the only public dataset supported by five is the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp). This data can be downloaded in-bulk as tabular data using the ``Congress`` or ``Congresses`` object. More granular control can be achieved by using a ``CongressMember`` object.

## Table of Contents<a name="table-of-contents"></a>

1) [Congress](#congress)
2) [Congresses](#congresses)
3) [CongressMember](#member)

***

## Congress<a name="congress"></a>

``Congress`` is used to query a single congress, and takes either a year or number to determine which congress to return.

For example, the following Congress objects all return the 116<sup>th</sup> US Congress:

``` python
a = v.Congress(116)
b = v.Congress(2019)
c = v.Congress(2020)
assert a.bioguide == b.bioguide == c.bioguide
```

Excluding a year or number will return the active US Congress:

``` python
c = v.Congress()
assert c.number == 116
```

### *.load()*

When ``Congress`` is instantiated, it will attempt to immediately load the requested data. To prevent this, the ``load_immediately`` flag can be set to ``False``. From there, you can use ``load()`` to download the data when you are ready, like so:

``` python
c = v.Congress(116, load_immediately=False)
c.load()
```

*Note: querying a transition year favors the congress that began that year (eg ``Congress(2015)`` will return the 114<sup>th</sup> congress, not the 113<sup>th</sup>).*

### *.bioguide*

The ``bioguide`` property on a ``Congress`` object returns Bioguide data as a ``BioguideCongressRecord``:

``` python
c = v.Congress(116)
print(c.bioguide)
```
```
{"members": [{ .. }], "congress_number": 116, "start_year": 2019, "end_year": 2021}
```

### *.members*

The ``members`` property on a ``Congress`` object returns a ``list`` of unique ``CongressMember`` objects:

``` python
c = v.Congress(116)
print(c.members[0].bioguide_id)
```
```
S001165
```

[Return to top](#table-of-contents)

***

## Congresses<a name="congresses"></a>

``Congresses`` is similiar to ``Congress``, but as the name suggests, it's meant to be a more easy route for querying many congresses at the same time.

``` python
c = v.Congresses(114, 116)
```

``Congresses`` can also query by year:

``` python
c = v.Congresses(2015, 2020)
```

*Note: year ranges that begin on a transition year only return the congress that began that year* (eg ``Congress(2015, 2020)`` *will include the 114<sup>th</sup> congress, but not the 113<sup>th</sup>.)*


### *.load()*

Calling the ``load`` method will download the chosen congress datasets.

### *.to_list()*

The ``to_list()`` method converts a ``Congresses`` object to a ``list`` of ``Congress`` objects.

### *.bioguides*

The ``bioguides`` member returns the chosen data as a list of bioguide records.

### *.members*

Due to the tendency of US Congress members to be re-elected, the ``members`` property of a ``Congresses`` object will return unique members across all returned congresses.


[Return to top](#table-of-contents)

***

## CongressMember<a name="member"></a>

The ``CongressMember`` class exists for querying data from the perspective of members. ``CongressMember`` is a much faster option for when you know the specific member(s) you would like to download data for.

*Examples Coming Soon*

[Return to top](#table-of-contents)
