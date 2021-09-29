import imaplib

from flask import Flask, request, redirect, render_template, url_for, session
from email_validator import EmailNotValidError, validate_email

app = Flask(__name__)
app.secret_key = "REPLACE THIS SECRET KEY"


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
            # Validate given email address is a valid email address.
            # Throws error if the email address is not valid.
            validate_email(email)

            # Open a connection with gmail.com and validate
            # user's email address and password
            inbox = imaplib.IMAP4_SSL("imap.gmail.com")
            inbox.login(email, password)
            inbox.logout()
        except EmailNotValidError as e:
            error = str(e)
        except imaplib.IMAP4.error as e:
            error = "Failed to authenticate with gmail.com"
            
            # Close connection after failing to authenticate with gmail.com
            inbox.logout()

    return render_template("login.html", error=error)

if __name__ == "__main__":
    app.run(debug=True)