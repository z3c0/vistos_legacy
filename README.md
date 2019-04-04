
# Five #

five is a module for downloading data on US politicians, and is designed to be used in conjunction with Pandas. You can import this module by placing the project in the root of your application and importing it like you would any module:

```python
import pandas as pd
import five as v

congress_df = pd.DataFrame(v.get_congress(116))
congress_df.to_csv('congress_members.csv')

```
