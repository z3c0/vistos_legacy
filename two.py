"""Legislative"""
from .web import bioguide as bio


class Congresses:
	def __init__(self, start=1, end=None):
		# load Bioguides
		self.bioguide = []
		for bioguide in bio.congress_iter(start, end):
			self.bioguide += bioguide


class Congress:
	def __init__(self, number_or_year):
		# load Bioguide
		query = bio.BioguideQuery(congress=number_or_year)
		r = query.send(clean_response=True)
		self.bioguide = r.data


class CongressMember:
	def __init__(self, last_name, first_name, position, state, year):
		pass