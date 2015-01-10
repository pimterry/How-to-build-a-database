import os, json, logging, cherrypy
from blist import sorteddict
from flask import Flask, abort, request, make_response

class Database:
    def __init__(self):
        self.data = sorteddict()
        self.keys = self.data.keys()
        self.values = self.data.values()

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data[key]

    def get_range(self, start_key, end_key):
        start_index = self.keys.bisect_left(start_key)
        end_index = self.keys.bisect_right(end_key)

        return self.values[start_index:end_index]

    def get_by(self, field_name, field_value):
        for value in self.values:
            try:
                if value[field_name] == field_value:
                    return value
            except KeyError:
                pass
        raise KeyError()

    def clear(self):
        self.data.clear()

def build_app():
  app = Flask(__name__)
  app.debug = True

  database = Database()

  @app.route("/reset", methods=["POST"])
  def reset():
      database.clear()
      return make_response("", 200)

  @app.route("/<int:item_id>", methods=["GET"])
  def get_item(item_id):
    try:
      return json.dumps(database.get(item_id))
    except KeyError:
      raise abort(404)

  @app.route("/range")
  def get_range():
    start, end = int(request.args.get('start')), int(request.args.get('end'))
    return json.dumps(database.get_range(start, end))

  @app.route("/<int:item_id>", methods=["POST"])
  def post_item(item_id):
    value = json.loads(request.data.decode('utf-8'))
    database.put(item_id, value)
    return make_response(str(value), 201)

  @app.route("/by/<field_name>/<field_value>")
  def query_by_field(field_name, field_value):
    parsed_value = json.loads(field_value)

    try:
        return json.dumps(database.get_by(field_name, parsed_value))
    except KeyError:
        raise abort(404)

  return app

def run_server(app):
    cherrypy.tree.graft(app, '/')

    cherrypy.config.update({
        'server.socket_port': int(os.environ.get('PORT', '8080')),
        'server.socket_host': '0.0.0.0'
    })
    cherrypy.log.error_log.setLevel(logging.WARNING)

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    app = build_app()
    run_server(app)
