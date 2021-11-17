from flask import Flask, session, redirect, url_for
from flaskr.auth import bp as auth_blueprint
from flaskr.bullymail import bp as bullymail_blueprint


def create_app(test_config = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping({
        "SECRET_KEY": "REPLACE THIS SECRET KEY"
    })

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(bullymail_blueprint)

    @app.route("/")
    def home():
        if "user" in session:
            return redirect(url_for("inbox.inbox"))
        return redirect(url_for("auth.login"))

    return app

