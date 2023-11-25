from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from absen.plugins import current_user
from sqlalchemy import desc, select
from absen.models import Classroom, Presence, User, db
from werkzeug.security import check_password_hash
from sqlalchemy import func

bp = Blueprint("schooldata", __name__, url_prefix="/school")


@bp.get("/")
def index():
    classrooms = current_user.school_admin.classrooms  # type: ignore
    class_id = request.args.get("class")
    date_str = request.args.get("date", "")

    query = None
    try:
        d = date.fromisoformat(date_str)
        print(class_id, d)
        query = db.session.execute(
            select(Presence)
            .filter(
                Presence.classroom_id == class_id,
                func.DATE(Presence.dt) == d,
            )
            .join(User, Presence.student_id == User.id)
        ).scalars()
    except Exception:
        pass

    # print(list(query))
    return render_template(
        "pages/school/index.html",
        classrooms=classrooms,
        attendances=query,
    )
