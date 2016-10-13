from datetime import datetime
import arrow


def conv_to_str(value):
    if isinstance(value, datetime):
        return arrow.get(value).format("MMMM D, YYYY")
    else:
        return unicode(value)


def isfloat(value):
    if value is None:
        return False
    try:
        float(value)
        return True
    except ValueError:
        return False


def first(lst):
    return next((x for x in lst if x), None)


def dget(d, dkey, default=None):
    """Dictionary get: gets the field from nested key

    Args:
        d (dict, list): Dictionary/list to retrieve field from
        dkey (str): Nested key to retrive field from dictionary/list separated 
            by periods. Example: key1.3.key2, this will be the equivalent of 
            d['key1'][3]['key2'].
        default (optional): Default object to return if value not found. 
            Defaults to None.

    Returns:
        Any: field to return from dict or default if not found.
    """
    keys = dkey.split('.')
    obj = d

    for key in keys:
        if not obj:
            return default
        if key.isdigit():
            index = int(key)
            if isinstance(obj, list) and index < len(obj):
                obj = obj[index]
            else:
                return default
        else:
            if isinstance(obj, dict) and key in obj:
                obj = obj[key]
            else:
                return default
    return obj
