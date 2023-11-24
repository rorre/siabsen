from os import environ
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import select

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

    app.register_blueprint(index_bp)

    return app
