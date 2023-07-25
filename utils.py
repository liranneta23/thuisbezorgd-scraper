import json

import numpy as np


def save_list_into_txt_file(list, file_name):
    # Sample array
    my_list = np.array(list)

    # Write the array to the file using numpy.savetxt()
    np.savetxt(file_name, my_list, fmt='%s')


def read_list_from_txt_file(file_name):
    # Read the data from the file using numpy.loadtxt()
    list_from_file = np.loadtxt(file_name, dtype=str)
    return list_from_file


def save_dictionary_fo_file(dict, file_name):
    # Serialize the dictionary as JSON
    json_data = json.dumps(dict)

    # Write the JSON data to the file
    with open(file_name, "w") as file:
        file.write(json_data)


def load_json_into_dictionary(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        return data
