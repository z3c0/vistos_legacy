

class API(object):
	def __init__(self, api_name, api_key_dict):
		for i, name in enumerate(api_key_dict['name']):
			if name == api_name:
				self.name = api_key_dict['name'][i]
				self.header = api_key_dict['header'][i]
				self.key = api_key_dict['key'][i]
				self.full_string = api_key_dict['full_string'][i]


def refresh_api_pickle():
	api_dict = csv_to_dict('api.csv', seperator='\t')
	dict_to_pickle(api_dict, 'api.pickle')


def pickle_to_dict(path):
	import pickle

	with open(path, 'rb') as pickle_file:
		result = pickle.load(pickle_file)

	pickle_file.close()

	return result


def dict_to_pickle(dict_to_write, path):
	import pickle

	with open(path, 'wb') as pickle_file:
		pickle.dump(dict_to_write, pickle_file)
	
	pickle_file.close()


def csv_to_dict(path, seperator=','):
	result = dict()
	
	with open(path, 'r') as file:
		first_line = str(file.readline())
		headers = first_line.split(seperator)
	
		for line in file:
			values = line.split(seperator)
	
			for i, header in enumerate(headers):
				header = header.strip()
				value = values[i].strip()
				try:
					result[header] += value
				except KeyError:
					result[header] = [value]
	
	file.close()
	return result