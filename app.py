import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from werkzeug.utils import secure_filename

from flask import Flask, request, redirect, render_template, url_for, jsonify, session
from email_validator import EmailNotValidError, validate_email
from mailparser import parse_from_bytes
import os

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


@app.route("/inbox/")
def inbox():
    if "user" not in session:
        return redirect(url_for("home"))

    session["messagesUids"] = None

    return render_template("inbox.html")


@app.route("/process/inbox/fetch", methods=["POST"])
def process_inbox_fetch():
    messageUids = session["messagesUids"]

    # Login using user credientials
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    user = session["user"]
    imap.login(user[0], user[1])
    imap.select()

    # Fetch all Uids from the server if the messageUids is empty
    if messageUids is None:
        _, data = imap.search(None, "ALL")
        data = data[0].decode().split()
        data.reverse()
        messageUids = data
        session["receivedUids"] = messageUids[:]

    index = 0
    html_text = """"""
    while index < 5 and messageUids:
        index += 1
        uid = messageUids.pop(0)
        _, raw_data = imap.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE FROM)])")
        msg = parse_from_bytes(raw_data[0][1])

        msg_subject = msg.subject
        msg_date = msg.date
        msg_from = msg.from_[0]

        if msg_from[0]:
            msg_from = msg_from[0]
        else:
            msg_from = msg_from[1]

        html_text += """<article>
            <h2><a href="{}">{}</a></h2> <!-- Subject -->
            <p>{}</p> <!-- Date -->
            <p>{}</p> <!-- From -->
        </article>""".format(url_for("inbox_message", uid=uid), msg_subject, msg_date, msg_from)

    imap.close()
    imap.logout()

    session["messagesUids"] = messageUids

    return jsonify({"messagesDisplayed": 0, "text": html_text, "empty": len(messageUids) == 0})


@app.route("/process/inbox/search", methods=["POST"])
def process_inbox_search():
    search_query = request.form["search"]

    # Login using user credientials
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    user = session["user"]
    imap.login(user[0], user[1])
    imap.select()

    # Strip search query any whitespaces beginning before and ending after content
    search_query = search_query.strip()

    if search_query:
        _, data = imap.search(None, "SUBJECT \"%s\"" % search_query)
    else:
        _, data = imap.search(None, "ALL")

    imap.close()
    imap.logout()

    # Decode into strings and setup from newest to oldest messages
    data = data[0].decode().split()
    data.reverse()

    session["messagesUids"] = data
    session["receivedUids"] = data[:]

    return jsonify({"empty": len(data) == 0})


@app.route("/inbox/<int:uid>/")
def inbox_message(uid):
    # Redirect user to login if user information does not exist
    if "user" not in session:
        return redirect(url_for("login"))
    if int(uid) <= 0:
        return redirect(url_for("inbox"))

    if str(uid) in session["receivedUids"]:
        user = session["user"]
        subject = fetch_subject(user[0], user[1], "imap.gmail.com", uid)
        return render_template("message.html", uid=uid, subject=subject)
    return redirect(url_for("inbox"))


def fetch_subject(username, password, host, uid):
    inbox = imaplib.IMAP4_SSL(host)
    inbox.login(username, password)
    inbox.select("INBOX")

    # Fetch the raw mail data using the uid
    _, raw_data = inbox.fetch(str(uid), '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
    inbox.close()
    inbox.logout()

    subject = raw_data[0][1].decode()
    subject = subject.replace("\r\n", "").lstrip("Subject: ")

    return subject


def fetch_mail(username, password, host, uid):
    inbox = imaplib.IMAP4_SSL(host)
    inbox.login(username, password)
    inbox.select("INBOX")

    # Fetch the raw mail data using the uid
    _, raw_data = inbox.fetch(str(uid), '(RFC822)')

    inbox.close()
    inbox.logout()

    # Convert raw data into usable message and return message itself
    if raw_data[0]:
        msg = parse_from_bytes(raw_data[0][1])
        return msg

    # Returns None if the message does not exist
    return None


def get_message_users(users):
    temp = []
    for user in users:
        if user[0]:
            temp.append("{} <{}>".format(user[0], user[1]))
        else:
            temp.append(user[1])
    return ", ".join(temp)


@app.route("/process/inbox/message", methods=["POST"])
def process_inbox_message():
    uid = request.form["uid"]
    user = session["user"]

    msg = fetch_mail(user[0], user[1], "imap.gmail.com", uid)

    msg_to = get_message_users(msg.to)
    msg_from = get_message_users(msg.from_)

    plain_text = msg.text_plain
    html_text = msg.text_html
    text = ''

    if html_text:
        text = html_text[0]
    elif plain_text:
        text = plain_text[0]

    return jsonify({"subject": msg.subject, "from": msg_from, "to": msg_to, "date": msg.date, "text": text})


@app.route("/compose/", methods=["POST", "GET"])
def composition():
    # If the user is not in the session, return them to the login
    if "user" not in session:
        return redirect(url_for("home"))

    # Retrieve all the data from the form
    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        bodytext = request.form["emailbody"]
        files = request.files.getlist("infile")

        # Join the current working directory with saved files and create that folder
        attachmentdir = os.path.join(os.getcwd(), "savedfiles")
        os.makedirs(attachmentdir, exist_ok=True)

        # Check if the user uloaded a file, if not, set files to none
        if files[0].filename == "":
            files = None
        else:

            # Iterate over the list of files adding each one to the new directory
            for i in range(len(files)):
                # This code does not send the file if the filename is nor secure.
                files[i].save(os.path.join(attachmentdir, secure_filename(files[i].filename)))

        # Call function to send the message
        sendmessage(receiver, session["user"][0], session["user"][1], bodytext, subject, files, attachmentdir)

        return redirect(url_for("inbox"))

    return render_template("composition.html")


def sendmessage(receiver, sender, password, bodytext, subject, files, attachmentdir):
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
    email.attach(MIMEText(bodytext, 'html'))

    # If there are no files, there is no point in trying to attach them.
    if files != None:
        for i in range(len(files)):

            # Try to add the requested files to the email
            try:
                # Retrieve the path for the uploaded file
                outfile = open(os.path.join(attachmentdir, secure_filename(files[i].filename)), 'rb')

                # Create the content type
                emailattachment = MIMEBase('application', 'octate-stream')
                # Set the payload to the file's contents
                emailattachment.set_payload((outfile).read())
                # Encode the attachment in base64
                encoders.encode_base64(emailattachment)

                # Add the file's name as the attachment's header and attach the files to the draft
                emailattachment.add_header('Content-Disposition',
                                           "attachment; filename= %s" % secure_filename(files[i].filename))
                email.attach(emailattachment)

                # Close the file when finished
                outfile.close()
            except Exception as e:
                print(str(e))
    # Convert the email to a string
    emailbody = email.as_string()

    # Send the email and end the SMTP connection
    securecon.sendmail(sender, receiver, emailbody)
    securecon.quit()

    # Iterate over the temporary file and delete its' contents
    for file in os.listdir(attachmentdir):
        oldfile = os.path.join(attachmentdir, file)
        os.remove(oldfile)

    # Return true on success
    return True


@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)