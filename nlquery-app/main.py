import tornado.ioloop
import tornado.web
from tornado.options import define, options, parse_command_line
from nlquery.nlquery import NLQueryEngine
import os
import json

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")

nlquery = NLQueryEngine('localhost', 9000)

# https://gist.github.com/mminer/5464753
class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = json.loads(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                print '%s' % str(self.request.body)
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()

    def write_json(self):
        try:
            output = json.dumps(self.response)
        except TypeError as e:
            raise e

        self.write(output)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('home.html')

class QueryHandler(JsonHandler):
    def post(self):
        query = str(self.request.arguments['q'])
        resp = nlquery.query(query, format_='raw')

        if not resp:
            self.response['data'] = {}

        if resp.get('tree'):
            resp['tree'] = '<pre>'+resp['tree']+'</pre>'
        if resp.get('sparql_query'):
            resp['sparql_query'] = '<pre>'+resp['sparql_query']+'</pre>'

        self.response['data'] = resp
        self.write_json()

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/query", QueryHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True)

if __name__ == "__main__":
    parse_command_line()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()