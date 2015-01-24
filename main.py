import logging, cherrypy, blist, json
from flask import Flask, request, abort


class Database:
    def __init__(self, fields_to_index, columns):
        self.data = blist.sorteddict()

        self.indexes = { field_name: blist.sorteddict() for field_name in fields_to_index }
        self.columns = { field_name: blist.sorteddict() for field_name in columns }

    def get_item(self, item_id):
        return self.data[item_id]

    def put_item(self, key, value):
        old_value = self.data[key] if key in self.data else None

        self.data[key] = value
        self._update_metadata(key, value, old_value)

    def _update_metadata(self, key, value, old_value):
        for field_name in self.indexes:
            index = self.indexes[field_name]
            try:
                old_field_value = old_value[field_name]
                if index[old_field_value] == old_value:
                    del index[old_field_value]
            except (KeyError, TypeError):
                pass

            try:
                field_value = value[field_name]
                index[field_value] = value
            except (KeyError, TypeError):
                pass

        for field_name in self.columns:
            column = self.columns[field_name]
            try:
                if column[key] == old_value:
                    del column[key]
            except (KeyError, TypeError):
                pass

            try:
                field_value = value[field_name]
                column[key] = field_value
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

    def sum_field(self, field_name):
        if field_name in self.columns:
            column = self.columns[field_name]
            return sum(item for item in column.values())
        else:
            return sum(item[field_name] for item in self.data.values()
                                        if field_name in item)

    def reset(self):
        self.data.clear()
        for index in self.indexes.values():
            index.clear()
        for column in self.columns.values():
            column.clear()

def build_app():
    app = Flask(__name__)
    app.debug = True

    database = Database(["name"], ["cost"])

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

    @app.route("/sum/<field_name>")
    def sum_field(field_name):
        return json.dumps(database.sum_field(field_name))

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
