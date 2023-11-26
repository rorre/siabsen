from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user
from sqlalchemy import select
from absen.models import User, db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint("index", __name__, url_prefix="/")


@bp.get("/")
def index():
    return render_template("pages/index.html")


@bp.get("/setup")
def setup_page():
    if current_app.config.get("HAS_SETUP", False):
        return redirect(url_for("index.index"))
    return render_template("pages/firstrun.html")


@bp.post("/setup")
def setup():
    data = request.form
    name = data.get("name", "").strip()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    password_confirm = data.get("password_confirm", "").strip()

    if any(len(data) == 0 for data in [name, username, password, password_confirm]):
        flash("Fill in all fields!", "error")
        return redirect(url_for("index.setup_page"))

    if password != password_confirm:
        flash("Password and confirm does not match!", "error")
        return redirect(url_for("index.setup_page"))

    user = User(
        username=username,
        password=generate_password_hash(password),
        is_superadmin=True,
        name=name,
    )

    db.session.add(user)
    db.session.commit()

    flash("Registered successfully!")
    return redirect(url_for("index.index"))


@bp.get("/login")
def login_page():
    return render_template("pages/login.html")


@bp.post("/login")
def login():
    data = request.form
    username = data.get("username")
    password = data.get("password", "")

    user = db.session.execute(
        select(User).filter(User.username == username)
    ).scalar_one_or_none()

    if not user or not check_password_hash(user.password, password):
        flash("Invalid username or password")
        return redirect(url_for("index.login_page"))

    login_user(user)
    return redirect(url_for("index.index"))


@bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index.index"))
