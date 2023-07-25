from bson import ObjectId

from db import insert_new_restaurants
from postal_codes_amsterdam import save_links_of_postal_codes, THUISBEZORG_URL_AMSTERDAM
from restaurant_details import store_extra_details, AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON
from restaurants_amsterdam import store_restaurants_data, AMSTERDAM_RESTAURANTS_JSON
from utils import load_json_into_dictionary


if __name__ == "__main__":
    # First, save all the links of the restaurants in each postal code
    links = save_links_of_postal_codes(THUISBEZORG_URL_AMSTERDAM)

    # Then, store all the restaurants from all the postal codes in a dictionary (helps in avoiding duplicates as well)
    restaurants = {}  # all the restaurants will be stored here. The key is the slug. Helps to avoid duplicates
    store_restaurants_data(restaurants)

    # Then, store the extra details as well, and load into a new json file
    restaurants_dict = load_json_into_dictionary(AMSTERDAM_RESTAURANTS_JSON)
    store_extra_details(restaurants_dict, AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON)

    # Then, store it in the MongoDB collection called 'restaurants'
    # restaurants_to_insert_to_db = load_json_into_dictionary(AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON)
    # insert_new_restaurants(restaurants_to_insert_to_db)
