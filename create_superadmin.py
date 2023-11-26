from getpass import getpass
from absen.models import User
from app import app
from absen.models import db
from werkzeug.security import generate_password_hash

username = input("Username: ")
password = getpass("Password: ")
name = input("Name: ")

with app.app_context():
    user = User(
        username=username,
        password=generate_password_hash(password),
        is_superadmin=True,
        name=name,
    )

    db.session.add(user)
    db.session.commit()

print("OK.")
