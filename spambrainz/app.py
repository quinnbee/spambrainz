from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from typing import Dict
from .web.models import db
from .web.views import index
from .api.api import create_api_bp

toolbar = DebugToolbarExtension()


def create_app(config_object="spambrainz.config.Config"):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False, template_folder="web/templates")

    app.config.from_object(config_object)

    db.init_app(app)

    if app.debug:
        toolbar.init_app(app)
        # reset_debug_db()

    backend_setting = app.config["BACKEND"]

    if backend_setting == "dummy":
        from .backend.dummy import DummyBackend
        backend = DummyBackend()
    else:
        mbdb_uri = app.config["MB_DATABASE_URI"]
        from brainzutils.musicbrainz_db import init_db_engine
        init_db_engine(mbdb_uri)

        if backend_setting == "dbdummy":
            from .backend.db_dummy import DbDummyBackend
            backend = DbDummyBackend()
        else:
            from .backend.celery import CeleryBackend
            backend = CeleryBackend()

    app.register_blueprint(index.bp)
    app.register_blueprint(create_api_bp(backend, app.config["API_TOKEN"]), url_prefix=app.config["API_PREFIX"])

    return app
