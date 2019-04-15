
# Five #

five is a module for downloading data on US politicians, and is designed to be used in conjunction with Pandas. You can import this module by placing the project in the root of your application and importing it like you would any module.

Currently, five only supports querying the [Biographical Directory of the United States Congress](http://bioguide.congress.gov/biosearch/biosearch.asp).

```python

import five as v
import pandas as pd

# query the 116th Congress
congress = v.Congress(116)
congress_df = pd.DataFrame(congress.bioguide)
congress_df.to_csv('bioguide_116.csv')

# query the congress active in 1863
congress = v.Congress(1863)
congress_df = pd.DataFrame(congress.bioguide)
congress_df.to_csv('bioguide_1863.csv')

# query all congresses from 1800 to 1900
congresses = v.Congresses(1800, 1900)
congresses_df = pd.DataFrame(congresses.bioguide)
congresses_df.to_csv('bioguide_1800-1900.csv')

# query all congresses, excluding Continental Congress
congresses = v.Congresses()
congresses_df = pd.DataFrame(congresses.bioguide)
congresses_df.to_csv('bioguide_no_contcong.csv')

# query all congresses, including Continental Congress
congresses = v.Congresses(0)
congresses_df = pd.DataFrame(congresses.bioguide)
congresses_df.to_csv('bioguide_with_contcong.csv')

# loop over all congresses from 1850 to 1900, storing each in a seperate file
congresses = [(i, v.Congress(i, load_immediately=False)) for i in range(1850, 1902, 2)]
for year, congress in congresses:
    congress.load()
    congress_df = pd.DataFrame(congress.bioguide)
    congress_df.to_csv('bioguide_' + str(year) + '.csv')

```
