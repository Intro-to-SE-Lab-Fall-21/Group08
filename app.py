import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, redirect, render_template, url_for, session
from email_validator import EmailNotValidError, validate_email

app = Flask(__name__)
app.secret_key = "REPLACE THIS SECRET KEY"


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("inbox"))
    return redirect(url_for("login"))


@app.route("/login/", methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect(url_for("inbox"))

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

            # Store user's email and password after successful authenication
            session["user"] = [email, password]

            return redirect(url_for("inbox"))
        except EmailNotValidError as e:
            error = str(e)
        except imaplib.IMAP4.error as e:
            error = "Failed to authenticate with gmail.com"

            # Close connection after failing to authenticate with gmail.com
            inbox.logout()

    return render_template("login.html", error=error)


@app.route("/inbox/", methods=["POST", "GET"])
def inbox():
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        pass
    return render_template("inbox.html")


@app.route("/compose/", methods=["POST", "GET"])
def composition():
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        bodytext = request.form["emailbody"]

        sendmessage(receiver, session["user"][0], session["user"][1], bodytext, subject)

    return render_template("composition.html")


def sendmessage(receiver, sender, password, bodytext, subject):
    # Attempt to establish a secure connection with the SMTP server
    try:
        securecon = smtplib.SMTP('smtp.gmail.com', 587)
        securecon.starttls()
        securecon.ehlo()

        # Attempt to login to the user's account
        securecon.login(sender, password)

        # Handle the exception by informing the user of failure.
    except Exception as error:
        print(error)
        print("Failed to establish a secure connection with the SMTP server.")
        # Return false upon failure
        return False

    # Create a message with multiple parts
    email = MIMEMultipart()

    email['FROM'] = sender
    email['To'] = receiver
    email['Subject'] = subject

    # Attach the body of the email to the message
    email.attach(MIMEText(bodytext, 'plain'))

    emailbody = email.as_string()

    # Send the email and end the SMTP connection
    securecon.sendmail(sender, receiver, emailbody)
    securecon.quit()
    # Return true on success
    return True


@app.route("/logout/")
def logout():
    if "user" in session:
        session.pop("user")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)