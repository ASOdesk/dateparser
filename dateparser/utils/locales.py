import locale
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def uselocale(localename):
    category = locale.LC_ALL
    default = locale.getlocale()
    try:
        locale.setlocale(category, localename)
    except:
        pass
    yield
    locale.setlocale(category, default)


def strptime(datestring, dateformat, localename):
    with uselocale(localename):
        return datetime.strptime(datestring, dateformat)
