def uniq(data: list) -> list:
    return list(set(data))


def uniq_list(data: list) -> list:
    """
    Make a list to unique value
    :return:
    :rtype:
    :param data:
    :type data:
    :return: []
    :rtype: []
    """
    uniq_data = []
    for d in data:
        if d not in uniq_data:
            uniq_data.append(d)
    return uniq_data


def deep_merge(dict_from: dict, dict_to: dict) -> dict:
    """
    Returns a dict merged value of dict_from and dict_to
        Parameters:
            dict_from (dict): A dictionary value
            dict_to (dict): Another dictionary value
        Returns:
            dict (dict): Merged dict
    """
    keys1 = dict_to.keys()
    keys2 = dict_from.keys()
    for k in keys2:
        if k in keys1:
            dict_to_1 = dict_to[k]
            dict_from_1 = dict_from[k]
            if isinstance(dict_to_1, dict) and isinstance(dict_from_1, dict):
                dict_to_1 = deep_merge(dict_from_1, dict_to_1)
                dict_to[k] = dict_to_1
            elif isinstance(dict_to_1, list) and isinstance(
                dict_from_1,
                list,
            ):
                dict_to[k] = dict_to_1 + dict_from_1
            elif isinstance(
                dict_to_1,
                set,
            ) and isinstance(
                dict_from_1,
                set,
            ):
                dict_to[k] = list(dict_to_1) + list(dict_from_1)
            else:
                pass
        else:
            dict_to[k] = dict_from[k]
    return dict_to


def snakecase_to_camelcase(word: str) -> str:
    """
    Snake case to camelcase
    Args:
        word (str): a snake case string
    Returns:
         word(str): a camelcase string of word
    """
    return " ".join(word.split("_")).capitalize()


if __name__ == "__main__":
    d1: dict = {
        "/test": {"get": {"response": {}, "security": {}, "tags": [], "parameters": {}}}
    }

    d2: dict = {
        "/test": {
            "post": {"response": {}, "security": {}, "tags": [], "parameters": {}}
        }
    }
    res = deep_merge(d1, d2)

    print(res)
