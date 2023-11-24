from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_user
from sqlalchemy import select
from absen.models import User, db
from werkzeug.security import check_password_hash

bp = Blueprint("index", __name__, url_prefix="/")


@bp.get("/")
def index():
    return render_template("pages/index.html")


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
