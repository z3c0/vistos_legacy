
# quinque (V)

quinque (*k<sup>w</sup>een-k<sup>w</sup>ay*) is a module for downloading data on US politicians, with the overall goal of making political data more accessible to developers.

Want to get started? Jump to the [samples](#tutorial) below to learn how to set up quinque.

## Why "quinque"?

The label "quinque" is meant to be as much of a statement and guiding philosophy as it is a name. 

Within the US government, there are three branches designed to keep each other in check: [the Legislative](https://congress.gov/), [the Judicial](https://www.supremecourt.gov/), and [the Executive](https://twitter.com/realdonaldtrump). In the past, ["the Fourth Branch"](https://en.wikipedia.org/wiki/Fourth_branch_of_government) has unofficially denoted the collective of influential institutions outside of those three branches whom have a signifance impact on the formation of policy, including the media, special interest groups, the financial sector, and sometimes even US citizens (*eg* when voting or acting as a juror.) In an ideal sense, these institutions making up the 4th Branch would use their power to keep the other three banches from reaching a kind of trust where each branch concedes not to police the other branches in exchange for not being policed themselves. For example, media outlets keep politicians in check by reporting on their statements and decisions to citizens, thus creating a system of accountability. Likewise, special interest/lobbying groups try to keep the spotlight on certain sections of society, in order to assure that legislators are not overlooking a fringe group when drafting new laws. Doing so encures that the majority rule of democracy does not tread on those who may not have a large enough representation to protect themselves.

Unfortunately - like many things - this does not pan out so nicely in reality. Significant members of the 4th Branch would seek to utilize their power to bolster their own special interests that often stand opposed to the interests of US citizens, such as the spread of propaganda, invasive data-gathering to fuel [Bernaysian Propaganda](https://en.wikipedia.org/wiki/Edward_Bernays), and pressuring legislators to craft laws that benefit only a small portion of the populace at the cost of the majority.

Today, we live in a world that has been dubbed ["post-truth"](https://en.wikipedia.org/wiki/Post-truth), where the boundary of what is false and what is reality has become so blurred that one can hardly discern on their own the truth of any matter without seeing it themselves. 

Because of this, it's time that the 4th Branch falls under the same scrutiny as the other three branches.

## Which brings us to the point...

What does all of this talk about checks and balances have to do with the name of this project? 

"Quinque" is the latin word for the number 5, and is denoted by the Roman numeral "V" (and will be denoted here as such, henceforth). By taking this name, V is asserting the existence of a *fifth* branch - the citizens, aided by technology. The formation of this fifth branch is a milestone in American politics, marking the point where citizens realize the power that has been granted to them through decades of compounding technological advancements. Thanks to the current state of technology, the average American is individually empowered more than they ever have been before, and far more than the Founding Fathers could have anticipated. Because of this, the need of the "Original Three" branches bears reassessment - however, those branches cannot be counted on to assess their own need, as they have a conflicted interest in their continued existence. Furthermore, the 4th Branch has failed to provide an objective view into the effectiveness of the Orginal Three.

Thus, it is time that US citizens began this reassessment themselves. To do this, the political data will need to be made more easily obtainable. Streamlining the availability of this information is a small - but fundamental - step in the far-more-grand goal of creating a more politically-informed populace.

***

_**V's goal is to enable US citizens by providing an easier route for accessing the information necessary to hold public officials more accountable.
This will be accomplished by 1) utilizing public data sources to gather information about public officials, and 2) consolidating that information in a way that's easy to code around.**_

***

## So why Python?

This idea is meant to be the guiding thought for defining the scope of V - that is to say that anything that enables US citizens to access political data more easily can be considered within the scope of V. At the moment, the tangible result of this is a collection of Python-based classes that marry disparate data sources into more easily-managed objects. That doesn't mean that V is inherently Python-based and will never take another form. Nor does it mean that any of this is poised to change anytime soon. It just means that a Python library currently makes the most sense for realizing the overall goal of V, due to the popularity of Python and its ease of use. Ideally, V is to stay in perpetual development and will always be taking the form of what makes the most sense at the time.

## What can V do today?

Currently, V only supports Congressional data provided by the Government Publishing Office, via the "duo" submodule. Support for social media data and stocks are planned for implementation in the near future, after which, work on the submodule for the Executive branch will begin (named "unus"). Each major realease of V will denote the availability of a new submodule. This means that v4.0 will mark the availability of all four submodules, with all releases from hence being considered minor versions (v4.X). 

If you'd like to contribute to the project, or know of a useful data source, feel free to submit a pull request, or [email z3c0](z3c0@21337.tech).

***

# Setting up quinque<a name="tutorial"></a>

#### Sample Project Structure
``` 
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

# Using quinque

Currently, the only public datasets supported by quinque are the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp) and the [govinfo API](https://www.govinfo.gov/)*. This data can be downloaded in-bulk as tabular data using the ``Congress`` or ``Congresses`` object. More granular control can be achieved by using a ``CongressMember`` object.

*\[\*\] govinfo examples coming soon*

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
