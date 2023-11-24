from flask_admin import Admin
from flask_migrate import Migrate
from flask_login import LoginManager, current_user as original_current_user

from absen.models import User, db

admin = Admin(name="Absensi", template_mode="bootstrap4")
migrate = Migrate(db=db)
login_manager = LoginManager()
current_user: User = original_current_user  # type: ignore
