import requests, sys


class API(object):
    name = str()
    keys = dict()

    def __init__(self, api_name):
        refresh_api_pickle()
        api_key_dict = pickle_to_dict('five-api.pickle')

        self.name = api_name

        try:
            for i, key in enumerate(api_key_dict['key']):
                if api_key_dict['name'][i] == self.name:
                    self.keys[api_key_dict['header'][i]] = api_key_dict['key'][i]
        except KeyError:
            print("KeyError: five-api.tsv must contain the header row from the README.md with tab separated values")
            sys.exit(1)


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

    try:
        with open(path, 'r') as file:
            first_line = str(file.readline())
            headers = first_line.split(seperator)

            try:
                for line in file:
                    values = line.split(seperator)
                    for i, header in enumerate(headers):
                        header = header.strip()
                        value = values[i].strip()
                        try:
                            result[header] += [value]
                        except KeyError:
                            result[header] = [value]
            except IndexError:
                print("IndexError: five-api.tsv values must be tab separated.")
                return

        file.close()
        return result
    except FileNotFoundError:
        print("FileNotFoundError: No such file: five-api.tsv")
        return

def send_request(self, endpoint):
    headers = {k: v for k, v in self.keys.items()}

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        return
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        return
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        return
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else",err)
        return

    json = response.json()
    return json
