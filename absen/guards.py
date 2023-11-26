from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from flask import abort
from absen.plugins import current_user

P = ParamSpec("P")
TResponse = TypeVar("TResponse")


def superadmin_only(func: Callable[P, TResponse]):
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        if not current_user.is_superadmin:
            abort(403)

        return func(*args, **kwargs)

    return inner


def school_admin_only(func: Callable[P, TResponse]):
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        if not current_user.is_school_admin:
            abort(403)

        return func(*args, **kwargs)

    return inner


def student_only(func: Callable[P, TResponse]):
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs):
        if not current_user.is_student:
            abort(403)

        return func(*args, **kwargs)

    return inner
