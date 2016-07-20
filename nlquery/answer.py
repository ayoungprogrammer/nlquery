from datetime import datetime

class Answer(object):
    def __init__(self, query=None, data=None):
        self.query = query
        self.data = data
        self.params = {}
        self.tree = None

    def to_plain(self):
        if isinstance(self.data, list):
            return ', '.join([Answer.to_string(d) for d in self.data])
        else:
            return Answer.to_string(self.data)

    def to_dict(self):
        return {
            'plain': self.to_plain(),
            'query': self.query,
            'params': self.params,
            'tree': self.tree,
        }

    @staticmethod
    def to_string(value):
        if isinstance(value, datetime):
            return value.strftime('%B %d, %Y')
        else:
            return unicode(value)