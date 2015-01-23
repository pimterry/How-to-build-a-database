import logging, cherrypy, blist, json, pickle
from flask import Flask, abort, request, make_response


class Database:
    def __init__(self, fields_to_index, columns, db_filename=None):
        self.data = blist.sorteddict()
        self.indexes = { index: blist.sorteddict() for index in fields_to_index }
        self.columns = { column: blist.sorteddict() for column in columns }

        if db_filename:
            db_file = open(db_filename, 'r+b')
            saved_data = pickle.load(db_file)
            for key in saved_data:
                self.put_item(key, saved_data[key])

    def get_item(self, key):
        return self.data[key]

    def put_item(self, key, value):
        old_value = self.data[key] if key in self.data else None
        self.data[key] = value

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
                column[key] = value[field_name]
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
            raise RuntimeError("Attempt to query for non-indexed field")

    def sum(self, field_name):
        if field_name in self.columns:
            return sum(self.columns[field_name].values())
        else:
            return sum(item[field_name] for item in self.data.values())

    def reset(self):
        self.data.clear()
        for index in self.indexes.values():
            index.clear()
        for column in self.columns.values():
            column.clear()


def build_app(db_filename=None):
    app = Flask(__name__)
    app.debug = True

    database = Database(["name"], ["cost"], db_filename)

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
        return make_response("ok", 201)

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
    def sum(field_name):
        return json.dumps(database.sum(field_name))

    @app.route("/", methods=["POST"])
    def batch_upload():
        data = json.loads(request.data.decode('utf-8'))
        for key in data:
            database.put_item(key, data[key])
        return make_response("ok", 201)

    @app.route("/reset", methods=["POST"])
    def reset():
        database.reset()
        return make_response("ok", 200)

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
