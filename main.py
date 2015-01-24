import logging, cherrypy, blist
from flask import Flask


class Database:
    def __init__(self):
        pass


def build_app():
    app = Flask(__name__)
    app.debug = True

    @app.route("/reset", methods=["POST"])
    def reset():
        return ""

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
