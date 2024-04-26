def uniq(data: list) -> list:
    return list(set(data))


def uniq_list(data: list) -> list:
    uniq_data = []
    for d in data:
        if d not in uniq_data:
            uniq_data.append(d)
    return uniq_data


def deep_merge(dict_from: dict, dict_to: dict):
    keys1 = dict_to.keys()
    keys2 = dict_from.keys()
    for k in keys2:
        if k in keys1:
            dict_to_1 = dict_to[k]
            dict_from_1 = dict_from[k]
            if isinstance(dict_to_1, dict) and isinstance(dict_from_1, dict):
                dict_to_1 = deep_merge(dict_from_1, dict_to_1)
                dict_to[k] = dict_to_1
            elif isinstance(dict_to_1, list) and isinstance(dict_from_1, list, ):
                dict_to[k] = dict_to_1 + dict_from_1
            elif isinstance(dict_to_1, set, ) and isinstance(dict_from_1, set, ):
                dict_to[k] = list(dict_to_1) + list(dict_from_1)
            else:
                pass
        else:
            dict_to[k] = dict_from[k]
    return dict_to


def snakecase_to_camelcase(word: str):
    return ' '.join(word.split('_')).capitalize()


if __name__ == '__main__':
    d1 = {
        '/test': {
            'get': {
                'response': {},
                'security': {},
                'tags': [],
                'parameters': {}
            }
        }
    }

    d2 = {
        '/test': {
            'post': {
                'response': {},
                'security': {},
                'tags': [],
                'parameters': {}
            }
        }
    }
    res = deep_merge(d1, d2)

    print(res)
