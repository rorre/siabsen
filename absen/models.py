from datetime import datetime
from typing import TYPE_CHECKING
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Boolean, ForeignKey, MetaData
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


db = SQLAlchemy(model_class=Base)

if TYPE_CHECKING:
    BaseModel = Base
else:
    BaseModel = db.Model


class School(BaseModel):
    __tablename__ = "school"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    classrooms: Mapped[list["Classroom"]] = relationship(back_populates="school", cascade="all, delete")

    admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "user.id",
            use_alter=True,
            ondelete="SET NULL",
        ),
    )
    admin: Mapped["User"] = relationship(
        "User",
        back_populates="school_admin",
        foreign_keys=[admin_id],
    )

    def __str__(self):
        return self.name


class User(BaseModel):
    __tablename__ = "user"
    is_authenticated = True
    is_active = True
    is_anonymous = False

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    school_admin: Mapped["School | None"] = relationship(
        back_populates="admin",
        foreign_keys=[School.admin_id],
    )

    classroom_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classroom.id", ondelete="SET NULL"),
        nullable=True,
    )
    classroom: Mapped["Classroom | None"] = relationship(back_populates="students")

    school_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("school.id", ondelete="CASCADE"),
        nullable=True,
    )
    school: Mapped["School"] = relationship(foreign_keys=[school_id])

    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def is_school_admin(self):
        return self.school_admin is not None

    @property
    def is_student(self):
        return self.classroom is not None and not self.is_school_admin

    def get_id(self):
        return self.id

    def __str__(self):
        return self.name


class Classroom(BaseModel):
    __tablename__ = "classroom"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    students: Mapped[list["User"]] = relationship(back_populates="classroom")

    school_id: Mapped[int] = mapped_column(Integer, ForeignKey("school.id"))
    school: Mapped["School"] = relationship(back_populates="classrooms")

    def __str__(self):
        return self.name


class Presence(BaseModel):
    __tablename__ = "presence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey("school.id"))
    school: Mapped["School"] = relationship()

    classroom_id: Mapped[int] = mapped_column(Integer, ForeignKey("classroom.id"))
    classroom: Mapped["Classroom"] = relationship()

    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    student: Mapped["User"] = relationship()
    dt: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
