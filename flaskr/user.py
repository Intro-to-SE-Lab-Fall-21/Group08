from flask import request, url_for, session
from email_validator import EmailNotValidError, validate_email
from mailparser import parse_from_bytes
import imaplib


class User:

    def __init__(self, user, password):
        self.user = ""
        self.password = ""

    def validate(self, email, password):

        error = None
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

        except EmailNotValidError as e:
            error = str(e)
        except imaplib.IMAP4.error as e:
            error = "Failed to authenticate with gmail.com"

            # Close connection after failing to authenticate with gmail.com
            inbox.logout()

        return error

    def inboxfetch(self, user):

        messageUids = session["messagesUids"]

        # Login using user credientials
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
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
                </article>""".format(url_for("inbox.inbox_message", uid=uid), msg_subject, msg_date, msg_from)

        imap.close()
        imap.logout()

        session["messagesUids"] = messageUids

        return html_text, messageUids

    def inboxsearch(self):
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

        return data

    def processmessage(self):
        user = session["user"]
        userObj = User(user[0], user[1])

        uid = request.form["uid"]
        user = session["user"]

        msg = userObj.fetch_mail(user[0], user[1], "imap.gmail.com", uid)

        msg_to = userObj.get_message_users(msg.to)
        msg_from = userObj.get_message_users(msg.from_)

        plain_text = msg.text_plain
        html_text = msg.text_html
        text = ''

        if html_text:
            text = html_text[0]
        elif plain_text:
            text = plain_text[0]

        return msg.subject, msg_from, msg_to, msg.date, text

    # Henry's functions #
    def fetch_subject(self, username, password, host, uid):
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

    def fetch_mail(self, username, password, host, uid):
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

    def get_message_users(self, users):
        temp = []
        for user in users:
            if user[0]:
                temp.append("{} <{}>".format(user[0], user[1]))
            else:
                temp.append(user[1])
        return ", ".join(temp)

    # Henry's functions