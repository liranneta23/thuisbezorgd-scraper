import pymongo
from bson import ObjectId

# Convert the JSON data to a Python dictionary
from constants import MONGODB_USERNAME, MONGODB_PASSWORD, COLLECTION_NAME, DATABASE_NAME
from restaurant_details import AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON
from utils import load_json_into_dictionary

# MongoDB configuration
mongodb_url = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@thuisbezorgddatabase.vmkx8iu.mongodb.net/"


def connect_to_db():
    # Connect to MongoDB
    client = pymongo.MongoClient(mongodb_url)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    return client, collection


def insert_new_restaurants(restaurants):
    try:
        client, collection = connect_to_db()

        # Delete all documents in the collection, before inserting the updated ones
        result = collection.delete_many({})
        print("Number of documents deleted:", result.deleted_count)

        # Insert the JSON data of each restaurant as a document. Only the first 100, as a POC
        for restaurant_slug in list(restaurants.keys())[:100]:
            collection.insert_one(restaurants[restaurant_slug])

        # Close the MongoDB connection
        client.close()

    except Exception as e:
        print("Error has occurred while trying to insert new documents to the DB: ", e)


def get_menu_of_restaurant(restaurant_id):
    menu = []

    try:
        client, collection = connect_to_db()

        restaurant = collection.find_one({"_id": restaurant_id})
        if restaurant:
            food_categories = restaurant['food_categories']

            for category in food_categories:
                category_name = category['name']
                for product_id in category['productIds']:
                    product = restaurant['food_items'][product_id]
                    item_on_menu = {
                        'product_id': product_id,
                        'name': product['name'],
                        'category': category_name,
                        'prices': product['variants'][0]['prices']
                    }

                    menu.append(item_on_menu)

        else:
            print(f"No restaurant has been found with the id {restaurant_id}")

        # Close the MongoDB connection
        client.close()

    except Exception as e:
        print(f"Error has occurred while trying to construct the menu of the restaurant {restaurant_id} ", e)

    return menu


if __name__ == "__main__":
    restaurants = load_json_into_dictionary(AMSTERDAM_RESTAURANTS_FULL_DETAILS_JSON)
    print(restaurants)
    print(len(restaurants.keys()))
    print("These were the restaurants to add")

    insert_new_restaurants(restaurants)
    menu = get_menu_of_restaurant(ObjectId('64bfc1bea5d86aba0b952009'))
    print(menu)
