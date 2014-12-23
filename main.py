import os, logging
import cherrypy
from flask import Flask, abort, request, make_response

def build_app():
  app = Flask("My First Database")
  app.debug = True

  data_dict = { }

  @app.route("/<int:item_id>", methods=["GET"])
  def get_item(item_id):
    try:
      return "%s" % (data_dict[item_id],)
    except KeyError:
      raise abort(404)

  @app.route("/<int:item_id>", methods=["POST"])
  def post_item(item_id):
    value = int(request.data)
    data_dict[item_id] = value
    return make_response(str(value), 201)

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
