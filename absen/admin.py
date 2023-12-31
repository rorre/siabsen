from flask import flash
from flask_admin.contrib.sqla import ModelView, fields
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from wtforms import PasswordField, validators

from absen.models import Classroom, School, User, db
from absen.plugins import current_user


class SuperAdminModelView(ModelView):
    column_exclude_list = ["password"]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_superadmin


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (current_user.is_superadmin or current_user.school_admin is not None)


class SchoolAdminModelView(AdminModelView):
    def is_accessible(self):
        return current_user.is_authenticated and (
            not current_user.is_superadmin and current_user.school_admin is not None
        )

    def school_id_attrib(self):
        return User.school_id

    def get_query(self):
        query = self.model.query
        if current_user.school_admin is not None:
            query = query.filter(self.school_id_attrib() == current_user.school_admin.id)

        return query

    def get_count_query(self):
        if current_user.school_admin is None:
            return super().get_count_query()
        return (
            self.session.query(func.count("*"))
            .select_from(self.model)
            .filter(self.school_id_attrib() == current_user.school_admin.id)
        )


class SchoolModelView(SuperAdminModelView):
    form_extra_fields = {
        "admin": fields.QuerySelectField("Admin"),
    }

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.admin.query = db.session.query(User).all()
        form.classrooms.query = db.session.query(Classroom).filter(Classroom.school == form._obj)
        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.admin.query = db.session.query(User).all()
        form.classrooms.query = db.session.query(Classroom).filter(Classroom.school == form._obj)
        return form

    def validate_form(self, form):
        if not hasattr(form, "admin"):
            return super().validate_form(form)

        if form.admin.data and form.admin.data.school_admin and form._obj != form.admin.data.school_admin:
            flash("User is already admin in another school!", "error")
            return False

        if form.admin.data and form.admin.data.is_student:
            flash("User is a student!", "error")
            return False
        return super().validate_form(form)


class UserModelView(SuperAdminModelView):
    column_list = ("username", "name", "classroom", "school")
    form_excluded_columns = ("password",)

    def school_id_attrib(self):
        return User.school_id

    form_extra_fields = {
        "classroom": fields.QuerySelectField("Classroom", allow_blank=True),
        "school": fields.QuerySelectField("School", allow_blank=True),
        "user_password": PasswordField(),
    }

    def on_model_change(self, form, model, is_created):
        if form.user_password.data:
            pwhash = generate_password_hash(form.user_password.data)
            model.password = pwhash
        return super().on_model_change(form, model, is_created)

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.user_password.label.text = "Change User Password"
        form.classroom.query = db.session.query(Classroom)
        form.school.query = db.session.query(School)

        return form

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.user_password.label.text = "Password"
        form.user_password.validators = [validators.InputRequired()]
        form.classroom.query = db.session.query(Classroom)
        form.school.query = db.session.query(School)

        return form


class StudentModelView(SchoolAdminModelView):
    column_list = ("username", "name", "classroom")
    form_extra_fields = {
        "classroom": fields.QuerySelectField("Classroom", validators=[validators.InputRequired()]),
        "user_password": PasswordField(),
    }
    form_excluded_columns = ("is_superadmin", "school_admin", "school", "password")

    def school_id_attrib(self):
        return User.school_id

    def on_model_change(self, form, model, is_created):
        if model.user_password:
            pwhash = generate_password_hash(form.user_password.data)
            model.password = pwhash
        model.school = current_user.school_admin
        return super().on_model_change(form, model, is_created)

    def edit_form(self, obj=None):
        assert current_user.school_admin is not None

        form = super().edit_form(obj)
        form.classroom.query = db.session.query(Classroom).filter(Classroom.school_id == current_user.school_admin.id)
        form.user_password.label.text = "Change Password"
        form.user_password.validators = []

        return form

    def create_form(self, obj=None):
        assert current_user.school_admin is not None

        form = super().create_form(obj)
        form.classroom.query = db.session.query(Classroom).filter(Classroom.school_id == current_user.school_admin.id)
        form.user_password.label.text = "Password"
        form.user_password.validators = [validators.InputRequired()]

        return form


class ClassroomModelView(SuperAdminModelView):
    column_list = ("school", "name")

    def school_id_attrib(self):
        return Classroom.school_id

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


class ClassroomAdminModelView(SchoolAdminModelView):
    column_list = ("name",)
    form_excluded_columns = ("school",)

    def school_id_attrib(self):
        return Classroom.school_id

    def on_model_change(self, form, model, is_created):
        model.school = current_user.school_admin
        return super().on_model_change(form, model, is_created)
