import os
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        DROP TABLE IF EXISTS producto;
        DROP TABLE IF EXISTS usuario;

        CREATE TABLE usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE producto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            descripcion TEXT DEFAULT ''
        );
        """
    )
    default_user = "admin"
    default_pass = os.environ.get("DEMO_PASSWORD", "Itla2024!")
    db.execute(
        "INSERT INTO usuario (username, password_hash) VALUES (?, ?)",
        (default_user, generate_password_hash(default_pass)),
    )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Inicializa la base de datos."""
    init_db()
    click.echo("Base de datos inicializada.")
