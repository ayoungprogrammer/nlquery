from datetime import datetime
from utils import conv_to_str

class Answer(object):
    """Answer object that holds query data"""
    def __init__(self, query=None, data=None):
        self.query = query
        self.data = data
        self.params = {}
        self.tree = None

    def to_plain(self):
        if isinstance(self.data, list):
            return ', '.join([conv_to_str(d) for d in self.data])
        else:
            return conv_to_str(self.data)

    def to_dict(self):
        return {
            'plain': self.to_plain(),
            'query': self.query,
            'params': self.params,
            'tree': self.tree,
        }