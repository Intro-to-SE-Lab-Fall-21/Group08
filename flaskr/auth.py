from flask import Blueprint, render_template, url_for, redirect, session, request
from flaskr.user import User

bp = Blueprint("auth", __name__)


@bp.route("/login/", methods=["POST", "GET"])
def login():
    error = None
    if "user" in session:
        return redirect(url_for("inbox.inbox"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        userObj = User(email, password)
        error = userObj.validate(email, password)

        if error is None:
            return redirect(url_for("inbox.inbox"))

    return render_template("login.html", error=error)


@bp.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("home"))