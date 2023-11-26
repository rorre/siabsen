from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, url_for
from absen.guards import student_only
from absen.plugins import current_user
from sqlalchemy import desc, select
from absen.models import Presence, db

bp = Blueprint("attendance", __name__, url_prefix="/attendance")


@bp.get("/")
@student_only
def index():
    user_attendance = list(
        db.session.execute(
            select(Presence)
            .filter(Presence.student == current_user)
            .order_by(desc(Presence.dt))
        )
        .scalars()
        .all()
    )

    has_attended = False
    try:
        latest = user_attendance[0]
        has_attended = datetime.today().date() == latest.dt.date()
    except IndexError:
        pass

    return render_template(
        "pages/attendance/index.html",
        attendances=user_attendance,
        has_attended=has_attended,
    )


@bp.post("/attend")
@student_only
def mark_attendance():
    latest = (
        db.session.execute(
            select(Presence)
            .filter(Presence.student == current_user)
            .order_by(desc(Presence.dt))
        )
        .scalars()
        .first()
    )

    has_attended = False
    if latest:
        has_attended = datetime.today().date() == latest.dt.date()

    if has_attended:
        flash("You have attended today!", "error")
        return redirect(url_for("attendance.index"))

    presence = Presence(
        classroom=current_user.classroom,
        school=current_user.school,
        student=current_user,
    )

    db.session.add(presence)
    db.session.commit()

    flash("You have successfully marked attendance!")
    return redirect(url_for("attendance.index"))
