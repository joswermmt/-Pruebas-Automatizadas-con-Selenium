import os
from pathlib import Path

from flask import Flask

from . import db, routes


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-tarea4-cambiar-en-produccion"),
        DATABASE=str(Path(app.instance_path) / "inventario.sqlite3"),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    app.register_blueprint(routes.bp)

    with app.app_context():
        if not Path(app.config["DATABASE"]).exists():
            db.init_db()

    return app
