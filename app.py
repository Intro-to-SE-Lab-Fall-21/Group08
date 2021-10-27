from flask import Flask, redirect, render_template, jsonify, url_for, session, request
from BullyMail import BullyMail
from User import User

from auth import bp as auth_blueprint
from auth import login_required


app = Flask(__name__)
app.secret_key = "REPLACE THIS SECRET KEY"

app.register_blueprint(auth_blueprint)


@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("inbox"))
    return redirect(url_for("auth.login"))


@app.route("/inbox/")
@login_required
def inbox():
    session["messagesUids"] = None

    return render_template("inbox.html")


@app.route("/process/inbox/fetch", methods=["POST"])
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


@app.route("/process/inbox/search", methods=["POST"])
@login_required
def process_inbox_search():
    user = session["user"]

    user_obj = User(user[0], user[1])
    data = user_obj.search_inbox(request.form["search"])

    session["messagesUids"] = data
    session["receivedUids"] = data[:]

    return jsonify({"empty": len(data) == 0})


@app.route("/inbox/<int:uid>/")
@login_required
def inbox_message(uid):
    user = session["user"]
    user_obj = User(user[0], user[1])

    # Redirects to the inbox since UID can only be 1 to infinity
    if int(uid) <= 0:
        return redirect(url_for("inbox"))

    # Render the message if we have a uid in the session data
    if str(uid) in session["receivedUids"]:
        subject = user_obj.fetch_subject("imap.gmail.com", uid)
        return render_template("message.html", uid=uid, subject=subject)
    
    return redirect(url_for("inbox"))


@app.route("/process/inbox/message", methods=["POST"])
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
        "text": message_body[4]
    })


@app.route("/compose/", methods=["POST", "GET"])
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

        return redirect(url_for("inbox"))

    return render_template("composition.html")


@app.route("/forward/<int:uid>", methods=["POST", "GET"])
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

        return redirect(url_for("inbox_message", uid=uid))

    user_obj = User(user[0], user[1])
    msg = user_obj.fetch_mail("imap.gmail.com", uid)
    
    msg_text = ""
    if msg.text_html:
        msg_text = msg.text_html[0]
    elif msg.text_plain:
        msg_text = msg.text_plain[0]

    return render_template("forward.html", text=msg_text, uid=uid, subject=msg.subject)


if __name__ == "__main__":
    app.run(debug=True)