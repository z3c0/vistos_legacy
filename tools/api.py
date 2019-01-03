import requests


class API(object):
    name = str()
    keys = dict()

    def __init__(self, api_name):
        refresh_api_pickle()
        api_key_dict = pickle_to_dict('five-api.pickle')

        self.name = api_name
        for i, api in enumerate(api_key_dict['api']):
            if api == api_name:
                self.keys[api_key_dict['header'][i]] = api_key_dict['key'][i]


def refresh_api_pickle():
    api_dict = csv_to_dict('five-api.tsv', seperator='\t')
    dict_to_pickle(api_dict, 'five-api.pickle')


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
                    result[header] += [value]
                except KeyError:
                    result[header] = [value]

    file.close()
    return result


def send_request(self, endpoint):
    headers = {k: v for k, v in self.keys.items()}
    response = requests.get(endpoint, headers=headers)
    json = response.json()
    return json
