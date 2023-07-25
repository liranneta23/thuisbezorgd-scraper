import json
import time

import cloudscraper

from postal_codes_amsterdam import get_postal_codes_only
from utils import save_dictionary_fo_file

POSTAL_CODE_RESTAURANTS_URL = "https://cw-api.takeaway.com/api/v33/restaurants?postalCode={}&limit=0&isAccurate=true&filterShowTestRestaurants=false"
RESTAURANT_BY_SLUG_URL = "https://cw-api.takeaway.com/api/v33/restaurant?slug={}"

AMSTERDAM_RESTAURANTS_JSON = "amsterdam_restaurants.json"

# copied from the request sniffed via Fiddler
headers = {
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'accept-language': 'nl',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'x-requested-with': 'XMLHttpRequest',
    'x-language-code': 'nl',
    'x-session-id': '55f8423f-fc2e-4cc3-9bfe-84d6ffc37b0c',
    'x-country-code': 'nl',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.thuisbezorgd.nl',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.thuisbezorgd.nl/',
    'accept-encoding': 'gzip, deflate, br'}
payload = None


def get_restaurant_main_data(restaurant, current_postal_code):
    data_as_dictionary = {}
    data_as_dictionary['name'] = restaurant['brand']['name']
    data_as_dictionary['postal_codes'] = [
        current_postal_code]  # list, starting with the first postalcode / delivery area
    data_as_dictionary['price_range'] = restaurant['priceRange']
    data_as_dictionary['popularity'] = restaurant['popularity']
    data_as_dictionary['rating_value'] = restaurant['rating']['score']
    data_as_dictionary['rating_count'] = restaurant['rating']['votes']
    data_as_dictionary['cuisine_types'] = restaurant['cuisineTypes']
    data_as_dictionary['minimum_order_amount'] = restaurant['shippingInfo']['delivery']['minOrderValue']

    return data_as_dictionary


def get_data_of_restaurants_from_feed(restaurants_dict, base_url, postal_code):
    try:
        data_str = ''

        url = base_url.format(str(postal_code))
        print("URL to scrpae on: ", url)
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)

        # Convert bytes to a string
        data_str = response.content.decode("utf-8")

        # Load the JSON-formatted string into a dictionary
        data_dict = json.loads(data_str)

        restaurants = data_dict['restaurants']

        for restaurant in restaurants.values():
            slug = restaurant['primarySlug']
            # check if the current restaurant was not added yet, based on its slug
            if restaurants_dict.get(slug) is None:  # if not present yet
                restaurants_dict[slug] = get_restaurant_main_data(restaurant, postal_code)
                # add a field with the slug, to be kept in the separated document of each restaurant
                restaurants_dict[slug]['slug'] = slug

            else:  # if it exists, just append the postal code to the entry
                restaurants_dict[slug]['postal_codes'].append(postal_code)

    except Exception as error:
        print(f'Error occured in url: {base_url.format(postal_code)}', error)
        print("Access denied? ", "Access denied" in data_str)

        if "Access denied" in data_str:  # in case we face a rate limit, sleep for some time :)
            print("Ok... then take a nap and back to work soon!")
            time.sleep(60)
            get_data_of_restaurants_from_feed(restaurants_dict, base_url, postal_code)
            print("Now the call was successfully done! After sleeping :)")


def store_restaurants_data(restaurants):
    base_url = POSTAL_CODE_RESTAURANTS_URL
    postal_codes = get_postal_codes_only()
    print(f'Running on {len(postal_codes)} postal codes in Amsterdam...')

    for postal_code in postal_codes:
        get_data_of_restaurants_from_feed(restaurants, base_url, postal_code)
        print(len(restaurants.keys()))

    save_dictionary_fo_file(restaurants, AMSTERDAM_RESTAURANTS_JSON)
    return restaurants


if __name__ == "__main__":
    restaurants = {}  # all the restaurants will be stored here. The key is the slug. Helps to avoid duplicates
    store_restaurants_data(restaurants)
