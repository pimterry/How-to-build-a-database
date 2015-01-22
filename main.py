import os, json, logging, cherrypy, collections, pickle, requests, time
from blist import sorteddict
from threading import Thread, Event, RLock
from timeoutlock import TimeoutLock
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, abort, request, make_response


class DatabasePersistThread(Thread):
    def __init__(self, db):
        super().__init__()
        self.db = db

    def run(self):
        while True:
            self.db.persist_needed.wait()
            self.db.persist_changes()


class Database:
    def __init__(self, db_filename, fields_to_index=[], columns=[], cluster=[]):
        self.data = sorteddict()
        self.keys = self.data.keys()
        self.values = self.data.values()

        self.indexes = {field: sorteddict() for field in fields_to_index}
        self.columns = {field: sorteddict() for field in columns}

        self.lock = TimeoutLock(0.5)

        self._setup_cluster(cluster)
        self._setup_persistence(db_filename)

    def _setup_persistence(self, db_filename):
        self.db_file = None

        self.persist_needed = Event()
        self.persisted = Event()
        self.persisted.set()

        if db_filename:
            db_file = open(db_filename, 'r+b')
            if os.path.exists(db_filename) and os.path.getsize(db_filename) > 0:
                self.load_db(db_file)
            self.db_file = db_file

            DatabasePersistThread(self).start()

    def _setup_cluster(self, cluster):
        self.cluster = cluster
        self.data_for_server = {server: {} for server in self.cluster}

    def load_db(self, db_file):
        data = pickle.load(db_file)
        for k, v in data.items():
            self.put(k, v)

    def put(self, key, value):
        old_value = self.data[key] if key in self.data else None
        if old_value == value:
            return

        with self.lock:
            self.data[key] = value

            self.sync_change(key, value)

            try:
                self.sync_changes()
            except ValueError:
                # Failed to replicate -> probably conflict, so rollback
                self.data[key] = old_value
                for data in self.data_for_server.values():
                    data.clear()
                raise

            if isinstance(value, collections.Iterable):
                for field_name, index in self.indexes.items():
                    self._update_index(index, field_name, value, old_value)

                for field_name, column in self.columns.items():
                    self._update_column(column, key, field_name, value)

            if self.db_file:
                self.persisted.clear()
                self.persist_needed.set()

        self.persisted.wait()

    def is_replication_completed(self):
        return all(len(data) == 0 for data in self.data_for_server.values())

    def sync_change(self, key, value):
        for server in self.cluster:
            self.data_for_server[server][key] = value

    def sync_changes(self):
        with self.lock:
            while not self.is_replication_completed():
                for server in self.cluster:
                    data_to_sync = self.data_for_server[server]
                    if len(data_to_sync) == 0: continue

                    try:
                        for k, v in data_to_sync.items():
                            result = requests.post("%s/%s" % (server, k), json.dumps(v))
                            if result.status_code == 503:
                                raise ValueError("Conflict when replicating value")
                        data_to_sync.clear()
                    except requests.exceptions.RequestException: pass

    def persist_changes(self):
        if self.db_file is not None:
            self.db_file.seek(0)
            pickle.dump(self.data, self.db_file)

            self.db_file.flush()
            os.fsync(self.db_file.fileno())

            self.persist_needed.clear()
            self.persisted.set()

    def _update_index(self, index, field_name, new_value, old_value):
        if old_value:
            try:
                old_key_in_index = old_value[field_name]
                del index[old_key_in_index]
            except (KeyError, TypeError):
                pass
        try:
            key_in_index = new_value[field_name]
            index[key_in_index] = new_value
        except (KeyError, TypeError):
            pass

    def _update_column(self, column, key, field_name, new_value):
        if key in column:
            del column[key]

        if field_name in new_value:
            column[key] = new_value[field_name]

    def get(self, key):
        with self.lock:
            return self.data[key]

    def get_range(self, start_key, end_key):
        with self.lock:
            start_index = self.keys.bisect_left(start_key)
            end_index = self.keys.bisect_right(end_key)

            return self.values[start_index:end_index]

    def get_by(self, field_name, field_value):
        with self.lock:
            if field_name not in self.indexes:
                raise ValueError("Cannot query without an index for field %s" % field_name)

            index = self.indexes[field_name]
            return index[field_value]

    def sum(self, field_name):
        with self.lock:
            if field_name not in self.columns:
                raise ValueError("Cannot aggregate non-columnular data")

            return sum(self.columns[field_name].values())

    def clear(self):
        with self.lock:
            self.data.clear()
            for index in self.indexes.values():
                index.clear()
            for column in self.columns.values():
                column.clear()


def build_app(db_filename=None, cluster=[]):
    app = Flask(__name__)
    app.debug = True

    database = Database(db_filename, ["name"], ["value"], cluster)

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

        try:
            database.put(item_id, value)
            return make_response(str(value), 201)
        except (TimeoutError, ValueError):
            abort(503)

    @app.route("/", methods=["POST"])
    def post_items():
        data = json.loads(request.data.decode('utf-8'))
        with ThreadPoolExecutor(10) as executor:
            list(executor.map(lambda pair: database.put(pair[0], pair[1]), data))
        return make_response("", 201)

    @app.route("/by/<field_name>/<field_value>")
    def query_by_field(field_name, field_value):
        parsed_value = json.loads(field_value)
        try:
            return json.dumps(database.get_by(field_name, parsed_value))
        except KeyError:
            raise abort(404)

    @app.route("/sum/<field_name>")
    def sum(field_name):
        return make_response(str(database.sum(field_name)), 200)

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
