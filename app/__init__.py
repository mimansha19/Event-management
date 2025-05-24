# App factory pattern to initialize extensions and register blueprints
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flasgger import Swagger

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register all blueprints
    from app.routes import auth, events, collaboration, versioning
    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(events.bp, url_prefix="/api/events")
    app.register_blueprint(collaboration.bp, url_prefix="/api/events")
    app.register_blueprint(versioning.bp, url_prefix="/api/events")

    return app