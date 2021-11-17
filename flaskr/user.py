import imaplib

from flask import url_for
from email_validator import EmailNotValidError, validate_email
from mailparser import parse_from_bytes


class User:

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def validate(self):

        error = None
        try:
            # Validate given email address is a valid email address.
            # Throws error if the email address is not valid.
            validate_email(self.user)

            # Open a connection with gmail.com and validate
            # user's email address and password
            inbox = imaplib.IMAP4_SSL("imap.gmail.com")
            inbox.login(self.user, self.password)

        except EmailNotValidError as e:
            error = str(e)
        except imaplib.IMAP4.error as e:
            error = "Failed to authenticate with gmail.com"
        finally:
            # Close connection after failing to authenticate with gmail.com
            inbox.logout()

        return error

    def fetch_inbox(self, message_uids):
        # Login using user credientials
        imap = open_mailbox("imap.gmail.com", self.user, self.password)
        imap.select()
        print(imap.list())

        # Fetch all Uids from the server if the messageUids is empty
        received_uids = None
        if message_uids is None:
            _, data = imap.search(None, "ALL")
            data = data[0].decode().split()
            data.reverse()
            message_uids = data
            received_uids = message_uids[:]

        index = 0
        html_text = """"""
        while index < 5 and message_uids:
            index += 1
            uid = message_uids.pop(0)
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

        return html_text, message_uids, received_uids

    def fetch_drafts(self, message_uids):
        # Login using user credientials
        imap = open_mailbox("imap.gmail.com", self.user, self.password)
        imap.select("[Gmail]/Drafts")

        # Fetch all Uids from the server if the messageUids is empty
        received_uids = None
        if message_uids is None:
            _, data = imap.search(None, "ALL")
            data = data[0].decode().split()
            data.reverse()
            message_uids = data
            received_uids = message_uids[:]

        index = 0
        html_text = """"""
        while index < 5 and message_uids:
            index += 1
            uid = message_uids.pop(0)
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
                </article>""".format(url_for("inbox.draft_message", uid=uid), msg_subject, msg_date, msg_from)

        imap.close()
        imap.logout()

        return html_text, message_uids, received_uids

    def search_inbox(self, search_query):
        # Login using user credientials
        imap = open_mailbox("imap.gmail.com", self.user, self.password)
        imap.select("[Gmail]/Drafts")

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

        return data

    def search_drafts(self, search_query):
        # Login using user credientials
        imap = open_mailbox("imap.gmail.com", self.user, self.password)
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

        return data

    def process_message(self, uid):
        msg = self.fetch_mail("imap.gmail.com", uid)

        msg_to = self._get_message_users(msg.to)
        msg_from = self._get_message_users(msg.from_)

        plain_text = msg.text_plain
        html_text = msg.text_html
        text = ''

        if html_text:
            text = html_text[0]
        elif plain_text:
            text = plain_text[0]
        
        attachments = msg.attachments[:]

        return msg.subject, msg_from, msg_to, msg.date, text, attachments

    def process_draft(self, uid):

        msg = self.fetch_draft_body("imap.gmail.com", uid)

        msg_to = self._get_message_users(msg.to)
        msg_from = self._get_message_users(msg.from_)
        msg_subject = msg.subject

        if msg_to == "":
            msg_to = "N/A"
        if msg.subject == "":
            msg_subject = "N/A"
        if msg_to and msg.subject == "":
            msg_to = "N/A"
            msg_subject = "N/A"

        plain_text = msg.text_plain
        html_text = msg.text_html
        text = ''

        if html_text:
            text = html_text[0]
        elif plain_text:
            text = plain_text[0]

        attachments = msg.attachments[:]

        return msg_subject, msg_from, msg_to, msg.date, text, attachments

    # Henry's functions #
    def fetch_subject(self, host, uid):
        inbox = open_mailbox(host, self.user, self.password)
        inbox.select()

        # Fetch the raw mail data using the uid
        _, raw_data = inbox.fetch(str(uid), '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
        inbox.close()
        inbox.logout()

        subject = raw_data[0][1].decode()
        subject = subject.replace("\r\n", "").lstrip("Subject: ")

        return subject

    def fetch_mail(self, host, uid):
        inbox = open_mailbox(host, self.user, self.password)
        inbox.select()

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

    def fetch_draft_body(self, host, uid):
        inbox = open_mailbox(host, self.user, self.password)
        inbox.select("[Gmail]/Drafts")

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

    def _get_message_users(self, users):
        temp = []
        for user in users:
            if user[0]:
                temp.append("{} <{}>".format(user[0], user[1]))
            else:
                temp.append(user[1])
        return ", ".join(temp)


def open_mailbox(host, username, password):
    try:
        mailbox = imaplib.IMAP4_SSL(host)
        mailbox.login(username, password)
    except imaplib.IMAP4.error:
        return None
    return mailbox