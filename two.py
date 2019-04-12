"""Legislative"""
from . import gpo as gpo


class Congresses:
	def __init__(self, start=1, end=None):
		# load Bioguides
		self.bioguide = []
		for bioguide in gpo.congress_iter(start, end):
			self.bioguide += bioguide


class Congress:
	def __init__(self, number_or_year):
		# load Bioguide
		self.bioguide = gpo.get_bioguide(number_or_year)


class CongressMember:
	def __init__(self, last_name, first_name, position, state, year):
		pass