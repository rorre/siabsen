from os import environ
from flask import Flask, g, redirect, request, url_for
from dotenv import load_dotenv
from sqlalchemy import func, select

from absen.admin import (
    ClassroomAdminModelView,
    ClassroomModelView,
    SchoolModelView,
    StudentModelView,
    UserModelView,
)

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    app.config["FLASK_ADMIN_SWATCH"] = "Flatly"

    from absen.plugins import admin, migrate, login_manager
    from absen.models import db, User, School, Classroom

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.execute(
            select(User).filter(User.id == user_id)
        ).scalar_one_or_none()

    admin.init_app(app)
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)

    admin.add_view(UserModelView(User, db.session, endpoint="user"))
    admin.add_view(
        StudentModelView(
            User,
            db.session,
            endpoint="student",
            name="Student",
        )
    )
    admin.add_view(SchoolModelView(School, db.session))
    admin.add_view(
        ClassroomModelView(
            Classroom,
            db.session,
            endpoint="classroomsuperadmin",
        )
    )
    admin.add_view(
        ClassroomAdminModelView(
            Classroom,
            db.session,
            endpoint="classroomadmin",
        )
    )

    from absen.routes.index import bp as index_bp
    from absen.routes.attendance import bp as attendance_bp
    from absen.routes.school import bp as school_bp

    app.register_blueprint(index_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(school_bp)

    @app.before_request
    def check_setup():
        has_setup: bool = app.config.get("HAS_SETUP", False)
        if has_setup:
            return

        if request.path.startswith("/setup"):
            return

        result = db.session.execute(
            select(func.count(User.id)).filter(User.is_superadmin == True)  # noqa: E712
        ).scalar_one()

        app.config["HAS_SETUP"] = result != 0
        if result != 0:
            return

        return redirect(url_for("index.setup_page"))

    return app
