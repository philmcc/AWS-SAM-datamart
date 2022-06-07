


def get_api_data(event, context):
    registry_data = get_rand_registry_data()
    rand_index = get_rand_price_index()




def get_rand_registry_data():

    api_result = requests.get(
        'https://europe-west2-wayhome-data-engineer-test.cloudfunctions.net/rand-registry-prices')
    data = json.dumps(api_result.json())
    rand_registry_dict = json.loads(data)['results']

    try:
        for house in rand_registry_dict:
            print('Address: ' + house['address'] + ' - City: ' + house['city'] + ' - Date: ' + house[
                'date'] + ' - Price: ' + str(house['price']))
    except Exception:
        pass

    return rand_registry_dict



def get_rand_price_index():

    api_result = requests.get(
        'https://europe-west2-wayhome-data-engineer-test.cloudfunctions.net/random-price-index')
    data = json.dumps(api_result.json())
    rand_price_index_dict = json.loads(data)['results']

    try:
        for city in rand_price_index_dict:
            print(city)
    except Exception:
        pass

    return rand_price_index_dict





