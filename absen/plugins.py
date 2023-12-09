from flask_admin import Admin, AdminIndexView
from flask_migrate import Migrate
from flask_login import LoginManager, current_user as original_current_user

from absen.models import User, db

admin = Admin(
    name="SiAbsen",
    template_mode="bootstrap4",
    index_view=AdminIndexView(name="Home", template="admin/home.html", url="/admin"),
)
migrate = Migrate(db=db)
login_manager = LoginManager()
current_user: User = original_current_user  # type: ignore
