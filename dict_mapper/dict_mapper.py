import re
from typing import Dict, Iterable, Any, Union, List, Callable


# def Pipeline(steps: DMStep):
#     return True


def dict_mapper(
        data: Union[Dict, Iterable[Dict]],
        mapper_options: Dict[str, Union[str, Callable]]
) -> Union[Dict, Iterable[Dict]]:
    """
    Map data into a dict or an iterable of dicts
    :param data:
    :param mapper_options:
    :return:
    """
    if isinstance(data, Dict):
        # return dict_mapper_covert(data, mapper_options)
        # Apply key mapper
        data = dict_mapper_covert(data, mapper_options)
        return data

    elif isinstance(data, list):
        return [
            dict_mapper(item, mapper_options)
            for item in data
        ]
    else:
        return data

@DeprecationWarning
def dict_mapper_covert_recursive(data: Dict, mapper_options: Dict) -> Dict:
    """
    Map data in a dict
    :param data:
    :param mapper_options:
    :return:
    """
    for key, value in data.items():
        # recursion
        if isinstance(value, dict):
            data[key] = dict_mapper_covert_recursive(value, mapper_options)
        elif isinstance(value, Iterable):
            data[key] = dict_mapper_covert_recursive(value, mapper_options)

        # change data

    return data


def dict_mapper_covert(data: Dict, mapper_options: Dict) -> Dict:
    # ??? add dict values? f(check(key), data.add = change(key,value))
    if 'update_mapper' in mapper_options:
        updates = {k: apply_update_mapper(k, v, mapper_options['update_mapper']) for k, v in data.items()}
        for old_key, update in updates.items():
            # update = {add: {}, remove_key: true}
            if update:
                data.update(update)
                # if update.remove_key:
                print("old_key '" + old_key + "', update = { " + str(update) + "}")
                del data[old_key]

    print("---------------")
    print(data)
    print("---------------")

    # Change Key = f(check(key), key = change(key))
    if 'key_mapper' in mapper_options:
        data = {apply_key_mapper(k, mapper_options['key_mapper']): v for k, v in data.items()}

    # Change value = f(check(key), value = change(value))
    if 'value_mapper' in mapper_options:
        data = {k: apply_value_mapper(k, v, mapper_options['value_mapper']) for k, v in data.items()}

    # Change value f(check(key), value = change(key,value)
    if 'item_mapper' in mapper_options:
        data = {k: apply_item_mapper(k, v, mapper_options['item_mapper']) for k, v in data.items()}

    return data


def apply_update_mapper(key: str, value: str, mapper_options: Dict[str, Union[str, Callable]]) -> Any:
    result = apply_mapper(key, value, mapper_options, lambda f, k, d: f(k, d))
    print("apply_update_mapper")
    print(result)
    if not result == value:
        return result


def apply_item_mapper(key: str, value: str, mapper_options: Dict[str, Union[str, Callable]]) -> Any:
    return apply_mapper(key, value, mapper_options, lambda f, k, d: f(k, d))


def apply_value_mapper(key: str, value: str, mapper_options: Dict[str, Union[str, Callable]]) -> Any:
    return apply_mapper(key, value, mapper_options, lambda f, k, d: f(d))


def apply_key_mapper(key: str, key_mapper: Dict[str, Union[str, List[Callable]]]) -> Any:
    return apply_mapper(key, key, key_mapper, lambda f, k, d: f(d))


def apply_mapper(key: str, value: Any, key_mapper: Dict[str, Union[str, List[Callable]]], wrap: Callable) -> str:
    for pattern, mapper in key_mapper.items():
        print()
        print("key:" + key + " pattern:" + str(pattern))
        if pattern == '*' or re.match(pattern, key):
            if isinstance(mapper, str):
                print(key + ": " + str(value) + " := '" + mapper + "'")
                return mapper
            elif isinstance(mapper, list):
                result = value
                for mapper_func in mapper:
                    result = wrap(mapper_func, key, result)
                    print(key + ": " + value + " = []f():" + str(result))
                print(key + ": " + value + " = [f()]:" + str(result))
                return result
            elif isinstance(mapper, Callable):
                result = wrap(mapper, key, value)
                print(key + ": " + value + " = f():" + str(result))
                return result
            elif isinstance(mapper, re.Pattern):
                print("is regex")
                if mapper.match(value):
                    print("has a match")
                    print(mapper.pattern)
                    print(mapper.match(value).groupdict())
                    # TODO find out how to patch the data dict back :/
                    # RuntimeError: dictionary changed size during iteration
                    # `data.update(mapper.match(value).groupdict())`
                    # `return { "add": mapper.match(value).groupdict(), "remove_key": True }`
                    return mapper.match(value).groupdict()
                else:
                    print("has no match")
            else:
                print(key + ": " + str(value) + " no change - mapper is not type of str/list[callable]/callable ")
                return value
    return value
