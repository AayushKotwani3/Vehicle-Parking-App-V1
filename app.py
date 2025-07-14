from flask import Flask
from Application.database import db
app=None

def create_app():
    # global app
    app=Flask(__name__)
    # app.secret_key="supersecretkey890"
    app.debug=True
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///parkingapp.sqlite" 
    db.init_app(app)

    with app.app_context():
        import Application.controllers

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
 