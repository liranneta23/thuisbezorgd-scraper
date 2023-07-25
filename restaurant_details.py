import json
import time

import cloudscraper
import asyncio

from restaurants_amsterdam import AMSTERDAM_RESTAURANTS_JSON
from utils import save_dictionary_fo_file, load_json_into_dictionary

RESTAURANT_BY_SLUG_URL = "https://cw-api.takeaway.com/api/v33/restaurant?slug={}"
AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON = "restaurants_amsterdam_full_details.json"

headers = {
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'accept-language': 'nl',
    'sec-ch-ua-mobile': '?0',
    'x-datadog-origin': 'rum',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'x-datadog-sampling-priority': '1',
    'accept': 'application/json, text/plain, */*',
    'x-requested-with': 'XMLHttpRequest',
    'x-session-id': 'cb19e9ee-5612-47ed-9075-d521ed50393a',
    'x-datadog-parent-id': '7777361851209639300',
    'x-language-code': 'nl',
    'x-country-code': 'nl',
    'x-datadog-trace-id': '3215877845003045879',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.thuisbezorgd.nl',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.thuisbezorgd.nl/',
    'accept-encoding': 'gzip, deflate, br'}
payload = None


def add_extra_details(current_restaurant_details, extra_details):
    current_restaurant_details['logo_link'] = extra_details['brand']['logoUrl']
    current_restaurant_details['website_url'] = extra_details['minisiteUrl']
    current_restaurant_details['street_name'] = extra_details['location']['streetName']
    current_restaurant_details['house_number'] = extra_details['location']['streetNumber']
    current_restaurant_details['delivery_times'] = extra_details['delivery']['times']
    current_restaurant_details['food_categories'] = extra_details['menu']['categories']
    current_restaurant_details['food_items'] = extra_details['menu']['products']


def get_extra_details_of_restaurant(restaurant_slug, base_url):
    try:
        data_str = ''

        url = base_url.format(restaurant_slug)
        print("URL to scrpae on: ", url)
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)

        data_str = response.content.decode("utf-8")
        data_dict = json.loads(data_str)

    except Exception as error:
        print(f'Error occured in url: {base_url.format(restaurant_slug)}', error)
        print("Access denied? ", "Access denied" in data_str)

        if "Access denied" in data_str:  # in case we face a rate limit, sleep for some time :)
            print("Ok... then take a nap and back to work soon!")
            time.sleep(60)
            return get_extra_details_of_restaurant(restaurant_slug, base_url)

        else:
            return None

    return data_dict


def store_extra_details(restaurants_dict, file_name):
    # due to rate limit --> I brought the results only for the first 20 restaurants. It would take 2 hrs for all :(
    for slug in list(restaurants_dict.keys())[:50]:
        extra_details = get_extra_details_of_restaurant(slug, RESTAURANT_BY_SLUG_URL)
        if extra_details:  # if error did not occur
            add_extra_details(restaurants_dict[slug], extra_details)
        # print(restaurants_dict[slug])

    # save the updated dictionary into the json which contains the full details about the restaurants
    save_dictionary_fo_file(restaurants_dict, file_name)

    # for the concurrency, we can use this (should be fixed)
    # asyncio.get_event_loop().run_until_complete(.....)


if __name__ == "__main__":
    restaurants_dict = load_json_into_dictionary(AMSTERDAM_RESTAURANTS_JSON)
    store_extra_details(restaurants_dict, AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON)
