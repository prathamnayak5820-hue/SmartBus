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

    # Import all models
    from .models import (
        User,
        Student,
        ParentStudentLink,
        Bus,
        Route,
        BoardingPoint,
        Trip,
        GPSLocation,
        PresenceEvent,
        AttendanceRecord,
        Notification,
        SOSEvent,
        NetworkEvent,
    )

    # Import routes
    from .routes.auth_routes import auth_bp
    from .routes.bus_routes import bus_bp
    from .routes.student_routes import student_bp
    from .routes.trip_routes import trip_bp
    from .routes.route_routes import route_bp

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )

    app.register_blueprint(
        bus_bp,
        url_prefix="/api/buses"
    )

    app.register_blueprint(
        student_bp,
        url_prefix="/api/students"
    )

    app.register_blueprint(
        trip_bp,
        url_prefix="/api/trips"
    )
    
    app.register_blueprint(
    route_bp,
    url_prefix="/api/routes"
    )

    @app.get("/")
    def home():
        return {
            "message": "SMART BUS backend is running",
            "status": "success"
        }

    return app