import logging
import requests

class ApiAdapter:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

    def format_log(self, format_str, *args, **kwargs):
        if len(args) + len(kwargs) == 0:
            return format_str
        if kwargs.get('_format') is False:
            return format_str
        return format_str.format(*args, **kwargs)

    def info(self, format_str, *args, **kwargs):
        msg = self.format_log(format_str, *args, **kwargs)
        self.logger.info(msg)

    def warn(self, format_str, *args, **kwargs):
        msg = self.format_log(format_str, *args, **kwargs)
        self.logger.warn(msg)

    def debug(self, format_str, *args, **kwargs):
        msg = self.format_log(format_str, *args, **kwargs)
        self.logger.debug(msg)

    def error(self, format_str, *args, **kwargs):
        msg = self.format_log(format_str, *args, **kwargs)
        self.logger.error(msg)


class RestAdapter(ApiAdapter):

    def get(self, url, params={}, headers=None, format_='json'):
        try:
            response = requests.get(url, params=params, headers=headers)
        except requests.exceptions.ConnectionError:
            print 'ConnectionError'
            return None
        self.info(response.url, _format=False)

        if format_ == 'json':
            try:
                json_data = response.json()
            except ValueError:
                json_data = None
                self.warn('Could not decode json properly')
            return json_data
        else:
            return response.text


class LibraryAdapter(ApiAdapter):
    pass
