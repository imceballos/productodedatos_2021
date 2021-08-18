import logging

# import os

from flask import Flask, has_request_context, request, render_template
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_caching import Cache

# TODO implement logger


cors = CORS()
db = SQLAlchemy()
bcrypt = Bcrypt()
cache = Cache()


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
        else:
            record.url = None

        return super().format(record)


def config_logger():
    formatter = RequestFormatter(
        "[%(asctime)s] level: %(levelname)s message: %(message)s"
    )

    default_handler.setFormatter(formatter)


def register_blueprints(app):
    from main.api import api_bp, api
    from flask_restx import apidoc

    # if not in testing enviroment (stage, prod)
    # change the url prefix for static files eg: swagger-ui.css
    if app.config["HOST_PATH"] != "":

        @apidoc.apidoc.add_app_template_global
        def swagger_static(filename):
            return "{0}/swaggerui/{1}".format("/some-path", filename)

        @api.documentation
        def custom_ui():
            return render_template(
                "swagger-ui.html",
                title=api.title,
                specs_url="{}/swagger.json".format(app.config["HOST"]),
            )

    app.register_blueprint(api_bp)


def create_app(app_settings):
    config_logger()
    app = Flask(__name__)

    app.config.from_object(app_settings)

    # NAPI_HOST_PATH represents the path where the app is mounted
    # for stage and prod env it should be /some-path

    cors.init_app(app)

    # Databases setup
    db.init_app(app)

    bcrypt.init_app(app)

    # Redis Cache
    #cache.init_app(app, config=app.config.get("REDIS_CONFIG"))

    # Blueprints setup
    register_blueprints(app)

    return app
