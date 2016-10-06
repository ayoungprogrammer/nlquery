import logging
import grequests

class LoggingInterface:
    """Interface for logging methods"""
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        self.logger.addHandler(ch)

    def format_log(self, format_str, *args, **kwargs):
        """Formats a string for logging"""

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


class RestAdapter(LoggingInterface):
    """Adapter for an Rest API endpoint

    Comes with logging methods
    """

    def get(self, url, params={}, headers=None, format_='json'):
        """Calls the get method for a REST endpoint. 

        Args:
            url (str): URL of endpoint
            params (url): params for endpoint
            headers (dict, optional): any additional header attrs. Default to None
            format_ (str, optional): Format requested. Default to json

        Returns:
            dict: Response of request if format is json
            str: Response of request if format is not json
        """
        try:
            greq = grequests.get(url, params=params, headers=headers)
            response = grequests.map([greq])[0]
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
