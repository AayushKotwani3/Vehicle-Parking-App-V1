# Imports the main Flask class to create the application instance, and the SQLAlchemy 'db' object
# from a local 'database' module. The 'app' variable is initialized to None, a common practice
# before creating the application instance using a factory pattern.
from flask import Flask
from Application.database import db
app=None

# This function follows the Application Factory pattern. It encapsulates the creation
# and configuration of the Flask application. This approach is beneficial for testing,
# managing configurations, and avoiding circular import problems.
def create_app():
    # Creates an instance of the Flask application. '__name__' helps Flask locate templates and static files.
    app=Flask(__name__)
    # Enables debug mode, which provides helpful error messages and automatically reloads the server on code changes.
    app.debug=True
    # Configures the database connection URI. In this case, it's set to a local SQLite database file.
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///parkingapp.sqlite" 
    # Initializes the SQLAlchemy extension by binding it to the Flask app instance.
    db.init_app(app)

    # The application context is pushed to make the application's configuration and extensions
    # (like 'db') available. This is necessary before importing modules like controllers
    # that might depend on the application being configured.
    with app.app_context():
        import Application.controllers

    # Returns the fully configured Flask application instance.
    return app

# This line calls the factory function to create the application instance. The returned
# object is assigned to the 'app' variable, which can then be used by a WSGI server.
app = create_app()

# This is the standard entry point for a Python script. The code inside this block
# will only execute when the script is run directly (e.g., `python main.py`).
# It will not run if the script is imported as a module into another file.
if __name__ == "__main__":
    # Starts the built-in Flask development web server to run the application.
    app.run()