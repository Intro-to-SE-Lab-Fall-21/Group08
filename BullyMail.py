from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from User import *
import smtplib
import os


class BullyMail:

    def __init__(self, receiver, subject, bodytext, files):
        self.receiver = receiver
        self.subject = subject
        self.bodytext = bodytext
        self.files = files

    def sendmessage(self, receiver, sender, password, bodytext, subject, files, attachmentdir):
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

    def compose(self):
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
        self.sendmessage(self.receiver, session["user"][0], session["user"][1], self.bodytext, self.subject, self.files,
                         attachmentdir)

