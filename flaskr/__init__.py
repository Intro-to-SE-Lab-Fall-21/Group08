from flask import Flask, session, redirect, url_for
from flaskr import auth, inbox

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    @app.route("/")
    def home():
        if "user" in session:
            return redirect(url_for("inbox.inbox"))
        return redirect(url_for("auth.login"))

    app.register_blueprint(auth.bp)
    app.register_blueprint(inbox.bp)

    return app