import copy


def keys_values(dictionary):
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    return keys + values


def find_element(dictionary, element):
    if element in list(dictionary.keys()):
        return element
    return dictionary.get(element)


def deepcopy(dictionary):
    return copy.deepcopy(dictionary)