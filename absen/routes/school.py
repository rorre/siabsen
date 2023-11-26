from datetime import date
from flask import Blueprint, render_template, request
from absen.guards import school_admin_only
from absen.plugins import current_user
from sqlalchemy import select
from absen.models import Presence, User, db
from sqlalchemy import func

bp = Blueprint("schooldata", __name__, url_prefix="/school")


@bp.get("/")
@school_admin_only
def index():
    classrooms = current_user.school_admin.classrooms  # type: ignore
    class_id = request.args.get("class")
    date_str = request.args.get("date", "")

    query = None
    try:
        d = date.fromisoformat(date_str)
        query = db.session.execute(
            select(Presence)
            .filter(
                Presence.classroom_id == class_id,
                func.DATE(Presence.dt) == d,
            )
            .join(User, Presence.student_id == User.id)
            .order_by(User.name)
        ).scalars()
    except Exception:
        pass

    return render_template(
        "pages/school/index.html",
        classrooms=classrooms,
        attendances=query,
    )
