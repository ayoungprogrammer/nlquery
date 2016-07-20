import arrow
import os


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


def first_return(functions, **args):
    for f in functions:
        ans = f(**args)
        if ans:
            return ans
    return None


def dget(d, dkey, default=None):
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


def starts_with_any(sent, arr):
    for word in arr:
        if sent[:len(word)].lower() == word:
            return True
    return False


def get_env():
    return os.environ.get('ENV', 'dev')


def calc_age(time):
    if not time:
        return None

    try:
        born = arrow.get(time)
    except arrow.parser.ParserError:
        print 'Error parsing time: {0}'.format(time)
        return None
    today = arrow.now()
    return str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))
