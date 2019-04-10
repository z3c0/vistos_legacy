
# Five #

five is a module for downloading data on US politicians, and is designed to be used in conjunction with Pandas. You can import this module by placing the project in the root of your application and importing it like you would any module:

```python

import five as v
import pandas as pd

congress = v.Congress(116)
congress.download_bioguide()

congress_df = pd.DataFrame(congress.bioguide)
congress_df.to_csv('bioguide.csv')

```
