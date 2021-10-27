import functools
from flask import Blueprint
from flask import url_for, redirect, render_template
from flask import request, session
from user import User


bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "user" not in session:
            return redirect(url_for("home"))
        return view(**kwargs)
    
    return wrapped_view


@bp.route("/login/", methods=["POST", "GET"])
def login():
    error = None
    if "user" in session:
        return redirect(url_for("inbox"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user_obj = User(email, password)
        error = user_obj.validate()
        if error is None:
            session["user"] = [email, password]
            return redirect(url_for("inbox"))

    return render_template("login.html", error=error)


@bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("home"))