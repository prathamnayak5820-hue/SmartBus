from flask import Flask
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, jwt, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)

    # Import models so SQLAlchemy knows them
    from .models import (
        user,
        student,
        parent_student_link,
        bus,
        route,
        boarding_point,
        trip,
        gps_location,
        presence_event,
        attendance_record,
        notification,
        sos_event,
        network_event,
    )

    # Register routes
    from .routes.auth_routes import auth_bp
    from .routes.bus_routes import bus_bp
    from .routes.student_routes import student_bp
    from .routes.trip_routes import trip_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(bus_bp, url_prefix="/api/buses")
    app.register_blueprint(student_bp, url_prefix="/api/students")
    app.register_blueprint(trip_bp, url_prefix="/api/trips")

    @app.get("/")
    def home():
        return {
            "message": "SMART BUS backend is running",
            "status": "success"
        }

    return app