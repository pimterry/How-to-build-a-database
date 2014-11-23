import os
import cherrypy
from flask import Flask, abort, request

def build_app():
  app = Flask("My First Database")
  app.debug = True

  data_dict = { }

  @app.route("/<item_id>", methods=["GET"])
  def get_item(item_id):
    try:
      return "%s" % (data_dict[item_id],)
    except KeyError:
      raise abort(404)

  @app.route("/<item_id>", methods=["POST"])
  def post_item(item_id):
    data_dict[item_id] = int(request.data)
    return "ok"

  return app

def run_server(app):
    cherrypy.tree.graft(app, '/')

    cherrypy.config.update({
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': int(os.environ.get('PORT', '8080')),
        'server.socket_host': '0.0.0.0'
    })

    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    app = build_app()
    run_server(app)
