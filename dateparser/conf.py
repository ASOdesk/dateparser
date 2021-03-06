# -*- coding: utf-8 -*-
import hashlib
from pkgutil import get_data
from functools import wraps
import six

from yaml import load as load_yaml, FullLoader

from .utils import registry


@registry
class Settings(object):
    """Control and configure default parsing behavior of dateparser.
    Currently, supported settings are:

    * `PREFER_DATES_FROM`: defaults to `current_period`. Options are `future` or `past`.
    * `SUPPORT_BEFORE_COMMON_ERA`: defaults to `False`.
    * `PREFER_DAY_OF_MONTH`: defaults to `current`. Could be `first` and `last` day of month.
    * `SKIP_TOKENS`: defaults to `['t']`. Can be any string.
    * `TIMEZONE`: defaults to `UTC`. Can be timezone abbreviation or any of `tz database name as given here <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`_.
    * `RETURN_AS_TIMEZONE_AWARE`: return tz aware datetime objects in case timezone is detected in the date string.
    * `RELATIVE_BASE`: count relative date from this base date. Should be datetime object.
    """

    _default = True
    _yaml_data = None

    def __init__(self, settings=None):
        if settings:
            self._updateall(settings.items())
        else:
            self._updateall(self._get_settings_from_yaml().items())

    @classmethod
    def get_key(cls, settings=None):
        if not settings:
            return 'default'

        keys = sorted(['%s-%s' % (key, str(settings[key])) for key in settings])
        return hashlib.md5(''.join(keys).encode('utf-8')).hexdigest()

    @classmethod
    def _get_settings_from_yaml(cls):
        if not cls._yaml_data:
            data = get_data('data', 'settings.yaml')
            cls._yaml_data = load_yaml(data, Loader=FullLoader).pop('settings', {})
        return cls._yaml_data

    def _updateall(self, iterable):
        for key, value in iterable:
            setattr(self, key, value)

    def replace(self, **kwds):
        for x in six.iterkeys(self._get_settings_from_yaml()):
            kwds.setdefault(x, getattr(self, x))

        kwds['_default'] = False

        return self.__class__(settings=kwds)


settings = Settings()


def apply_settings(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kwargs['settings'] = kwargs.get('settings', settings)

        if kwargs['settings'] is None:
            kwargs['settings'] = settings

        if isinstance(kwargs['settings'], dict):
            kwargs['settings'] = settings.replace(**kwargs['settings'])

        if not isinstance(kwargs['settings'], Settings):
            raise TypeError(
                "settings can only be either dict or instance of Settings class")

        return f(*args, **kwargs)
    return wrapper
