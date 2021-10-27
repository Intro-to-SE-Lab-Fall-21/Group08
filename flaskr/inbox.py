from flask import Blueprint, render_template, url_for, redirect, session, request, jsonify
from flaskr.user import User
from flaskr.bullymail import BullyMail

bp = Blueprint("inbox", __name__)


@bp.route("/inbox/")
def inbox():
    if "user" not in session:
        return redirect(url_for("home"))

    session["messagesUids"] = None

    return render_template("inbox.html")


@bp.route("/process/inbox/fetch", methods=["POST"])
def process_inbox_fetch():
    user = session["user"]

    # Here, emailbody is a tuple consisting of the html text and the message identifier
    userObj = User(user[0], user[1])
    emailbody = userObj.inboxfetch(user)

    return jsonify({"messagesDisplayed": 0, "text": emailbody[0], "empty": len(emailbody[1]) == 0})


@bp.route("/process/inbox/search", methods=["POST"])
def process_inbox_search():

    user = session["user"]

    userObj = User(user[0], user[1])
    data = userObj.inboxsearch()

    return jsonify({"empty": len(data) == 0})


@bp.route("/inbox/<int:uid>/")
def inbox_message(uid):
    user = session["user"]

    userObj = User(user[0], user[1])
    # Redirect user to login if user information does not exist
    if "user" not in session:
        return redirect(url_for("auth.login"))
    if int(uid) <= 0:
        return redirect(url_for("inbox.inbox"))

    if str(uid) in session["receivedUids"]:
        user = session["user"]
        subject = userObj.fetch_subject(user[0], user[1], "imap.gmail.com", uid)
        return render_template("message.html", uid=uid, subject=subject)
    return redirect(url_for("inbox.inbox"))


@bp.route("/process/inbox/message", methods=["POST"])
def process_inbox_message():
    user = session["user"]
    userObj = User(user[0], user[1])

    messagebody = userObj.processmessage()

    return jsonify({"subject": messagebody[0], "from": messagebody[1], "to": messagebody[2], "date": messagebody[3],
                    "text": messagebody[4]})


@bp.route("/compose/", methods=["POST", "GET"])
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

        bullyObj = BullyMail(receiver, subject, bodytext, files)
        result = bullyObj.compose()

        if result is False:
            return redirect(url_for("auth.logout"))
        else:
            return redirect(url_for("inbox.inbox"))

    return render_template("composition.html")


@bp.route("/forward/<int:uid>", methods=["POST", "GET"])
#consider uid as an argument in forward
def forward(uid):
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user = session["user"]
    userObj = User(user[0], user[1])

    msg = userObj.fetch_mail(session["user"][0], session["user"][1], "imap.gmail.com", uid)

    if request.method == "POST":
        receiver = request.form["receiver"]
        subject = request.form["subject"]
        bodytext = request.form["emailbody"]
        files = request.files.getlist("infile")

        bullyObj = BullyMail(receiver, subject, bodytext, files)
        result = bullyObj.compose()

        return redirect(url_for("inbox.inbox_message", uid=uid))

    msg_text = ""
    if msg.text_html:
        msg_text = msg.text_html[0]
    elif msg.text_plain:
        msg_text = msg.text_plain[0]

    return render_template("forward.html", text=msg_text, uid=uid, subject=msg.subject)