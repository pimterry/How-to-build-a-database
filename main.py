import logging, cherrypy, blist, json
from flask import Flask, request, abort


class Database:
    def __init__(self, fields_to_index):
        self.data = blist.sorteddict()

        self.indexes = { field_name: blist.sorteddict() for field_name in fields_to_index }

    def get_item(self, item_id):
        return self.data[item_id]

    def put_item(self, item_id, value):
        self.data[item_id] = value

        for field_name in self.indexes:
            index = self.indexes[field_name]
            try:
                field_value = value[field_name]
                index[field_value] = value
            except (KeyError, TypeError):
                pass

    def get_range(self, start, end):
        start_index = self.data.keys().bisect_left(start)
        end_index = self.data.keys().bisect_right(end)

        return self.data.values()[start_index:end_index]

    def get_by_field(self, field_name, field_value):
        if field_name in self.indexes:
            index = self.indexes[field_name]
            return index[field_value]
        else:
            raise RuntimeError("Attempt to query for non-indexed value")

    def reset(self):
        self.data.clear()

def build_app():
    app = Flask(__name__)
    app.debug = True

    database = Database(["name"])

    @app.route("/<int:item_id>")
    def get_item(item_id):
        try:
            return json.dumps(database.get_item(item_id))
        except KeyError:
            return abort(404)

    @app.route("/<int:item_id>", methods=["POST"])
    def put_item(item_id):
        value = json.loads(request.data.decode('utf-8'))
        database.put_item(item_id, value)
        return "ok"

    @app.route("/", methods=["POST"])
    def put_many_items():
        values = json.loads(request.data.decode('utf-8'))
        for key, value in values.items():
            database.put_item(key, value)
        return "ok"

    @app.route("/range")
    def get_range():
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))

        return json.dumps(database.get_range(start, end))

    @app.route("/by/<field_name>/<field_value>")
    def get_by_field(field_name, field_value):
        try:
            return json.dumps(database.get_by_field(field_name, field_value))
        except KeyError:
            return abort(404)

    @app.route("/reset", methods=["POST"])
    def reset():
        database.reset()
        return "ok"

    return app


def run_server(app, port=8080):
    cherrypy.tree.graft(app, '/')

    cherrypy.config.update({
        'server.socket_port': port,
        'server.socket_host': '0.0.0.0'
    })
    cherrypy.log.error_log.setLevel(logging.WARNING)

    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    app = build_app()
    run_server(app)
