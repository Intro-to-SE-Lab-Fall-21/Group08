from flask import Flask, request, redirect, render_template, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)