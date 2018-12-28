five is an API-wrapper for ProPublica's Congress API, and is designed to be used in conjunction with Pandas. You can import this module by placing the project in the root of your application and importing it like you would any module:

```python
import pandas as pd
import five as v

congress_df = pd.DataFrame(v.get_congress())
congress_df.to_csv('congress_members.csv')

```


To utilize this package, you must have a .TSV in the root of your application called "five-api.tsv" (for now). This file contains all the access keys needed for the APIs utilized by five. Naturally, this requires that you have access to any of the APIs being used. As new APIs are used, I'll update the table below to show them, including links to where keys can be obtained.

name | header | key
---- | ------ | ---
congress | X-API-Key | API key obtained from [ProPublica](https://www.propublica.org/datastore/api/propublica-congress-api)


Here's a copyable example:

```csv
name	header	key
congress	X-API-Key	yt0h9...f273rhf

```
