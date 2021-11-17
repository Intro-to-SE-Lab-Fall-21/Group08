from email.mime.multipart import MIMEMultipart
import imaplib
from werkzeug.utils import secure_filename
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import smtplib
import os


class BullyMail:

    def __init__(self, receiver, subject, bodytext, files):
        self.receiver = receiver
        self.subject = subject
        self.bodytext = bodytext
        self.files = files

    def send_message(self, receiver, sender, password, bodytext, subject, files, attachmentdir):
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

    def compose(self, user, password):
        # Join the current working directory with saved files and create that folder
        attachmentdir = os.path.join(os.getcwd(), "savedfiles")
        os.makedirs(attachmentdir, exist_ok=True)

        # Check if the user uloaded a file, if not, set files to none
        if self.files[0].filename == "":
            files = None
        else:

            # Iterate over the list of files adding each one to the new directory
            for i in range(len(self.files)):
                # This code does not send the file if the filename is nor secure.
                self.files[i].save(os.path.join(attachmentdir, secure_filename(self.files[i].filename)))

        # Call function to send the message
        self.send_message(self.receiver, user, password, self.bodytext, self.subject, self.files,
                         attachmentdir)


from flask import Blueprint
from flask import url_for, redirect, render_template, jsonify
from flask import request, session
from flaskr.user import User
from flaskr.auth import login_required


bp = Blueprint("inbox", __name__)


@bp.route("/inbox/")
@login_required
def inbox():
    session["messagesUids"] = None

    return render_template("inbox.html")


@bp.route("/process/inbox/fetch", methods=["POST"])
@login_required
def process_inbox_fetch():
    user = session["user"]

    # Here, emailbody is a tuple consisting of the html text and the message identifier
    user_obj = User(user[0], user[1])
    emailbody, message_uids, received_uids = user_obj.fetch_inbox(session["messagesUids"])
    
    session["messagesUids"] = message_uids
    if received_uids is not None:
        session["receivedUids"] = received_uids

    return jsonify({"messagesDisplayed": 0, "text": emailbody, "empty": len(emailbody) == 0})


@bp.route("/process/inbox/search", methods=["POST"])
@login_required
def process_inbox_search():
    user = session["user"]

    user_obj = User(user[0], user[1])
    data = user_obj.search_inbox(request.form["search"])

    session["messagesUids"] = data
    session["receivedUids"] = data[:]

    return jsonify({"empty": len(data) == 0})


@bp.route("/inbox/<int:uid>/")
@login_required
def inbox_message(uid):
    user = session["user"]
    user_obj = User(user[0], user[1])

    # Redirects to the inbox since UID can only be 1 to infinity
    if int(uid) <= 0:
        return redirect(url_for(".inbox"))

    # Render the message if we have a uid in the session data
    if str(uid) in session["receivedUids"]:
        subject = user_obj.fetch_subject("imap.gmail.com", uid)
        return render_template("message.html", uid=uid, subject=subject)
    
    return redirect(url_for(".inbox"))


@bp.route("/process/inbox/message", methods=["POST"])
@login_required
def process_inbox_message():
    user = session["user"]
    user_obj = User(user[0], user[1])

    message_body = user_obj.process_message(request.form["uid"])

    return jsonify({
        "subject": message_body[0], 
        "from": message_body[1], 
        "to": message_body[2], 
        "date": message_body[3],
        "text": message_body[4],
        "attachments" : message_body[5]
    })


@bp.route("/compose/", methods=["POST", "GET"])
@login_required
def composition():
    # Retrieve all the data from the form
    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        body_text = request.form["emailbody"]
        files = request.files.getlist("infile")

        bully_mail = BullyMail(receiver, subject, body_text, files)
        
        user = session["user"]
        result = bully_mail.compose(user[0], user[1])

        return redirect(url_for(".inbox"))

    return render_template("composition.html")


@bp.route("/forward/<int:uid>", methods=["POST", "GET"])
@login_required
def forward(uid):
    user = session["user"]

    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        body_text = request.form["emailbody"]
        files = request.files.getlist("infile")

        bully_mail = BullyMail(receiver, subject, body_text, files)

        user = session["user"]
        bully_mail.compose(user[0], user[1])

        return redirect(url_for(".inbox_message", uid=uid))

    user_obj = User(user[0], user[1])
    msg = user_obj.fetch_mail("imap.gmail.com", uid)
    
    msg_text = ""
    if msg.text_html:
        msg_text = msg.text_html[0]
    elif msg.text_plain:
        msg_text = msg.text_plain[0]

    return render_template("forward.html", text=msg_text, uid=uid, subject=msg.subject)


@bp.route("/delete/<int:uid>")
@login_required
def delete(uid):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(session["user"][0], session["user"][1])
    imap.select()
    
    str_uid = str(uid)
    imap.store(str_uid, "+FLAGS", "\\Deleted")
    imap.expunge()
    imap.close()
    imap.logout()

    return redirect(url_for(".inbox"))
