from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla import fields
from wtforms import SelectField
from absen.models import User, db
from sqlalchemy import select
from absen.models import Classroom, Presence, School
from absen.plugins import current_user
from werkzeug.security import generate_password_hash


class SuperAdminModelView(ModelView):
    column_exclude_list = ["password"]

    def is_accessible(self):
        return current_user.is_superadmin


class SchoolAdminModelView(ModelView):
    school_id_attrib = None

    def is_accessible(self):
        from absen.plugins import current_user

        return current_user.is_superadmin or current_user.school_admin is not None

    def get_query(self):
        query = self.model.query
        if not current_user.is_superadmin and current_user.school_admin is not None:
            query = query.filter(self.school_id_attrib == current_user.school_admin.id)

        return query


class SchoolModelView(SuperAdminModelView):
    form_extra_fields = {
        "admin": fields.QuerySelectField("Admin"),
    }

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.admin.query = db.session.query(User).all()
        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.admin.query = db.session.query(User).all()
        return form


class UserModelView(SchoolAdminModelView):
    school_id_attrib = User.school_id
    form_extra_fields = {
        "classroom": fields.QuerySelectField("Classroom", allow_blank=True),
        "school": fields.QuerySelectField("School", allow_blank=True),
    }

    def on_model_change(self, form, model, is_created):
        pwhash = generate_password_hash(form.password.data)
        model.password = pwhash
        return super().on_model_change(form, model, is_created)

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        query = db.session.query(Classroom)
        if current_user.school_admin is not None:
            query = query.filter(Classroom.school_id == current_user.school_admin.id)

        form.classroom.query = query
        form.school.query = db.session.query(School).all()
        if not current_user.is_superadmin:
            form.school.render_kw = {"readonly": True}

        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        query = db.session.query(Classroom)
        if current_user.school_admin is not None:
            query = query.filter(Classroom.school_id == current_user.school_admin.id)

        form.classroom.query = query
        form.school.query = db.session.query(School).all()
        if not current_user.is_superadmin:
            form.school.render_kw = {"readonly": True}

        return form


class ClassroomModelView(SchoolAdminModelView):
    school_id_attrib = Classroom.school_id
    form_extra_fields = {
        "school": fields.QuerySelectField("School"),
    }

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.school.query = db.session.query(School).all()
        if not current_user.is_superadmin:
            form.school.render_kw = {"readonly": True}
        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.school.query = db.session.query(School).all()
        if not current_user.is_superadmin:
            form.school.render_kw = {"readonly": True}

        return form
