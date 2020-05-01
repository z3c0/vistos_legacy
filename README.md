
# five

five is a module for downloading data on US politicians, with the overall goal of making political data more accessible to developers. You can import this module by placing the project in the root of your application and importing it like you would any module.

# Using five

Currently, the only public dataset supported by five is the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp). This data can be downloaded in-bulk as tabular data using the ``Congress`` or ``Congresses`` object. More granular control can be achieved by using a ``CongressMember`` object.

***

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
print(c.members)
```
```
[{'bioguide_id': 'W000822', 'first_name': 'Bonnie' .. sentative', 'state': 'CA', 'party': 'Democrat'}]}]
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

The ``CongressMember`` class exists for querying data from the perspective of members. When querying terms via ``Congresses``, you can expect to see members duplicated across terms, as congress people often serve many terms. The ``CongressMember`` class helps consolidate these terms into a single object per member. This can help to cut down the size of data, as unchanging personal details of a member (name, age, etc) are only stored once.

*Examples Coming Soon*

[Return to top](#table-of-contents)
