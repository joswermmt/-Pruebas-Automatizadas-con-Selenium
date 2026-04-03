from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("main", __name__)

# Límites para pruebas de límites (validación servidor)
NOMBRE_MAX_LEN = 80
CANTIDAD_MAX = 99999


def login_required(view):
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Debe iniciar sesión para continuar.", "warning")
            return redirect(url_for("main.login", next=request.path))
        return view(*args, **kwargs)

    wrapped.__name__ = view.__name__
    return wrapped


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        db = get_db()
        row = db.execute(
            "SELECT id, password_hash FROM usuario WHERE username = ?", (username,)
        ).fetchone()
        error = None
        if row is None:
            error = "Usuario o contraseña incorrectos."
        elif not check_password_hash(row["password_hash"], password):
            error = "Usuario o contraseña incorrectos."
        if error is None:
            session.clear()
            session["user_id"] = row["id"]
            session["username"] = username
            nxt = request.form.get("next") or request.args.get("next")
            if (
                not nxt
                or not nxt.startswith("/")
                or nxt.startswith("//")
            ):
                nxt = url_for("main.lista_productos")
            return redirect(nxt)
        flash(error, "danger")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.login"))


@bp.route("/")
def index():
    return redirect(url_for("main.lista_productos"))


@bp.route("/productos")
@login_required
def lista_productos():
    db = get_db()
    rows = db.execute(
        "SELECT id, nombre, cantidad, descripcion FROM producto ORDER BY id DESC"
    ).fetchall()
    return render_template("productos_lista.html", productos=rows)


@bp.route("/productos/nuevo", methods=("GET", "POST"))
@login_required
def producto_nuevo():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        cantidad_raw = request.form.get("cantidad", "0")
        errors = []
        if not nombre:
            errors.append("El nombre es obligatorio.")
        if len(nombre) > NOMBRE_MAX_LEN:
            errors.append(f"El nombre no puede superar {NOMBRE_MAX_LEN} caracteres.")
        try:
            cantidad = int(cantidad_raw)
        except (TypeError, ValueError):
            errors.append("La cantidad debe ser un número entero.")
            cantidad = 0
        else:
            if cantidad < 0:
                errors.append("La cantidad no puede ser negativa.")
            if cantidad > CANTIDAD_MAX:
                errors.append(f"La cantidad no puede superar {CANTIDAD_MAX}.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "producto_form.html",
                titulo="Nuevo producto",
                producto=None,
                nombre=nombre,
                descripcion=descripcion,
                cantidad=cantidad_raw,
            )
        db = get_db()
        db.execute(
            "INSERT INTO producto (nombre, cantidad, descripcion) VALUES (?, ?, ?)",
            (nombre, cantidad, descripcion),
        )
        db.commit()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("main.lista_productos"))
    return render_template(
        "producto_form.html",
        titulo="Nuevo producto",
        producto=None,
        nombre="",
        descripcion="",
        cantidad="0",
    )


@bp.route("/productos/<int:pid>/editar", methods=("GET", "POST"))
@login_required
def producto_editar(pid):
    db = get_db()
    row = db.execute(
        "SELECT id, nombre, cantidad, descripcion FROM producto WHERE id = ?", (pid,)
    ).fetchone()
    if row is None:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("main.lista_productos"))

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip()
        cantidad_raw = request.form.get("cantidad", "0")
        errors = []
        if not nombre:
            errors.append("El nombre es obligatorio.")
        if len(nombre) > NOMBRE_MAX_LEN:
            errors.append(f"El nombre no puede superar {NOMBRE_MAX_LEN} caracteres.")
        try:
            cantidad = int(cantidad_raw)
        except (TypeError, ValueError):
            errors.append("La cantidad debe ser un número entero.")
            cantidad = 0
        else:
            if cantidad < 0:
                errors.append("La cantidad no puede ser negativa.")
            if cantidad > CANTIDAD_MAX:
                errors.append(f"La cantidad no puede superar {CANTIDAD_MAX}.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template(
                "producto_form.html",
                titulo="Editar producto",
                producto=row,
                nombre=nombre,
                descripcion=descripcion,
                cantidad=cantidad_raw,
            )
        db.execute(
            "UPDATE producto SET nombre = ?, cantidad = ?, descripcion = ? WHERE id = ?",
            (nombre, cantidad, descripcion, pid),
        )
        db.commit()
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.lista_productos"))

    return render_template(
        "producto_form.html",
        titulo="Editar producto",
        producto=row,
        nombre=row["nombre"],
        descripcion=row["descripcion"] or "",
        cantidad=str(row["cantidad"]),
    )


@bp.route("/productos/<int:pid>/eliminar", methods=("POST",))
@login_required
def producto_eliminar(pid):
    db = get_db()
    cur = db.execute("DELETE FROM producto WHERE id = ?", (pid,))
    db.commit()
    if cur.rowcount:
        flash("Producto eliminado.", "success")
    else:
        flash("No se encontró el producto.", "warning")
    return redirect(url_for("main.lista_productos"))
