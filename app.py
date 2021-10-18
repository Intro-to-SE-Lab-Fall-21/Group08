import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, request, redirect, render_template, url_for, jsonify, session
from email_validator import EmailNotValidError, validate_email
from mailparser import parse_from_bytes

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


@app.route("/inbox/", defaults={"number": 0})
@app.route("/inbox/<int:number>", methods=["POST", "GET"])
def inbox(number):
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        pass
    
    # Open connection with the IMAP server
    inbox = imaplib.IMAP4_SSL("imap.gmail.com")
    
    # Login using the user's login information
    user = session["user"]
    inbox.login(user[0], user[1])
    
    # Get the message count
    _, response = inbox.select()
    latest_uid_number = int(response[0].decode())
    uid_number = latest_uid_number - (5 * number)

    msgs = []
    uids_str = []
    
    # Fetch last five messages until five messages are fetched
    # or message count goes to zero
    for i in range(uid_number, max(0, uid_number - 5), -1):
        _, raw_data = inbox.fetch(str(i), "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
        msg = parse_from_bytes(raw_data[0][1])
        msgs.append(msg)
        uids_str.append(i)
    inbox.close()
    inbox.logout()

    return render_template("inbox.html", 
        messages=msgs, 
        uids=uids_str, 
        number=number, 
        uid_number=uid_number, 
        latest_uid_number=latest_uid_number
        )


@app.route("/inbox/<int:inbox_page>?<int:uid>")
def inbox_message(uid, inbox_page):
    # Redirect user to login if user information does not exist
    if "user" not in session:
        return redirect(url_for("login"))
    if int(uid) <= 0:
        return redirect(url_for("inbox"))

    user = session["user"]
    msg = fetch_mail(user[0], user[1], "imap.gmail.com", uid)

    if msg:
        msg_subject = msg.subject
        msg_from = msg.from_[0]
        msg_to = msg.to[0]
        msg_date = msg.date
        msg_text = msg.text_plain

        if msg_from[0]:
            msg_from = msg_from[0]
        else:
            msg_from = msg_from[1]
        if msg_to[0]:
            msg_to = msg_to[0]
        else:
            msg_to = msg_to[1]

        if len(msg_text) == 0:
            msg_text = ""
        else:
            msg_text = msg_text[0]

        return render_template("message.html", 
            subject=msg_subject, 
            from_=msg_from, 
            to=msg_to, 
            date=msg_date, 
            text=msg_text, 
            inbox_page=inbox_page
            )
    return redirect(url_for("inbox"))


def fetch_mail(username, password, host, uid):
    inbox = imaplib.IMAP4_SSL(host)
    inbox.login(username, password)
    inbox.select("INBOX")
    
    # Fetch the raw mail data using the uid
    _, raw_data = inbox.fetch(str(uid), '(RFC822)')

    # Convert raw data into usable message and return message itself
    if raw_data[0]:
        msg = parse_from_bytes(raw_data[0][1])
        return msg
    
    # Returns None if the message does not exist
    return None
    

@app.route("/compose/", methods=["POST", "GET"])
def composition():
    if "user" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        bodytext = request.form["emailbody"]

        sendmessage(receiver, session["user"][0], session["user"][1], bodytext, subject)
        return redirect(url_for("inbox"))

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


@app.route("/inbox/search/")
def search():
    return render_template('search.html')


def fetch_messages(uid: list | str, mailbox: imaplib.IMAP4):
    if type(uid) is str:
        uid = [uid]
    uid = [i.decode() for i in uid]

    html_text = """"""
    for i in range(len(uid)):
        _, raw_data = mailbox.fetch(uid[i], "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])")
        msg = parse_from_bytes(raw_data[0][1])

        from_ = msg.from_[0][0] if msg.from_[0][0] else msg.from_[0][1]
        html_text += """<article>
        <h2><a id="{uid}" href="#">{subject}</a></h2>
        <p>{date}</p>
        <p>{from_}</p>
        <p id="{uid}-text"></p>
        </article>""".format(uid=uid[i], subject=msg.subject, date=msg.date, from_=from_)
    return uid, html_text


@app.route("/inbox/search/process", methods=["POST"])
def search_process():
    user_query = request.form["query"]
    
    if user_query:

        # Open connection with IMAP server using the user login info
        mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
        mailbox.login(session["user"][0], session["user"][1])
        mailbox.select()

        # Search on IMAP server with user query
        _, data = mailbox.search(None, 'SUBJECT \"' + user_query + '\"')
        data = data[0].split()

        # Returns "No messages found" if the query returns no messages
        if len(data) == 0:
            return jsonify({"error": "No messages found"})

        # Store session info about search
        session["search-index"] = index = 0
        session["search-uid"] = data

        # Fetch messages
        uid_data = data[-1-5*index:-6-5*index:-1]
        used_uids, html_text = fetch_messages(uid_data, mailbox)

        # Close the connection
        mailbox.close()
        mailbox.logout()

        can_next = not (abs(-1 - 5 * (index + 1)) > len(data))
        
        return jsonify({"htmlText": html_text, "canNext": can_next, "uids": used_uids})

    return jsonify({"error": "Missing data!"})


@app.route("/inbox/search/next", methods=["POST"])
def search_next():
    if "search-index" not in session:
        return jsonify({"error": "Cannot go next search!"})
    
    increment = int(request.form["value"])
    index = session["search-index"] + increment
    uids = session["search-uid"]

    # Open connection with IMAP server using the user login info
    mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    mailbox.login(session["user"][0], session["user"][1])
    mailbox.select()

    uids = uids[-1-5*index:-6-5*index:-1]
    used_uids, html_text = fetch_messages(uids, mailbox) 

    # Close the connection
    mailbox.close()
    mailbox.logout()

    # Update the index
    session["search-index"] = index

    can_next = not (abs(-1 - 5 * (index + 1)) > len(uids))
    can_prev = -1 - 5 * (index - 1) <= -1

    return jsonify({"htmlText": html_text, "canNext": can_next, "canPrev": can_prev, "uids": used_uids})


@app.route("/inbox/search/show", methods=["POST"])
def search_show_text():
    # Fetch text using the message id
    mailbox = imaplib.IMAP4_SSL("imap.gmail.com")
    mailbox.login(session["user"][0], session["user"][1])
    mailbox.select()
    uid = request.form["uid"]
    _, data = mailbox.fetch(uid, "(RFC822)")
    mailbox.close()
    mailbox.logout()
    
    # Parse into a message
    msg = parse_from_bytes(data[0][1])

    return jsonify({"text": msg.text_html})


@app.route("/logout/")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
