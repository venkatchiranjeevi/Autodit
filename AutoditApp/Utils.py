from collections import defaultdict
from django.db.models import QuerySet


def coalesce(*args):
    """
    Returns first not None value
    :param args: list|tuple
    :return: value
    """
    for arg in args:
        if arg is not None:
            return arg
    return None


def list_of_dict_to_dict(list_obj, dict_key):
    new_dict_obj = dict()
    if list_obj is None:
        return list_obj
    for list_item in list_obj:
        try:
            key = getattr(list_item, dict_key) if isinstance(list_obj, QuerySet) else list_item.get(dict_key, None)
            if key:
                new_dict_obj[key] = list_item
        except (ValueError, Exception) as e:
            pass
    return new_dict_obj
