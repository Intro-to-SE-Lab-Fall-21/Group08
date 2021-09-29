from flask import Flask, request, redirect, render_template, url_for
from email_validator import EmailNotValidError, validate_email

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            validate_email(email)
        except EmailNotValidError as e:
            error = str(e)
    return render_template("login.html", error=error)

if __name__ == "__main__":
    app.run(debug=True)