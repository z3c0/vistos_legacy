"""Legislative"""
from .web import bioguide as bio


class Congresses:
	def __init__(self):
		pass


class Congress:
	def __init__(self, number):
		self.number = number

	def download_bioguide(self, raw=False):
		self.bioguide = bio.get_congress(self.number, clean=not raw)


class CongressMember:
	def __init__(self):
		pass