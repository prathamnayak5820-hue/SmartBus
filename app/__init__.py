from flask import Flask
from flask_cors import CORS
from .routes.gps_routes import gps_bp
from .config import Config
from .extensions import db, migrate, jwt, bcrypt
from .routes.network_routes import network_bp
from .routes.presence_routes import presence_bp
from .routes.eta_routes import eta_bp
from .routes.geofence_routes import geofence_bp
from .routes.deviation_routes import deviation_bp
from .routes.source_routes import source_bp
from .routes.sync_routes import sync_bp


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

    app.register_blueprint(gps_bp, url_prefix="/api/gps")
    app.register_blueprint(network_bp, url_prefix="/api/network")

    app.register_blueprint(eta_bp, url_prefix="/api/eta")

    app.register_blueprint(geofence_bp, url_prefix="/api/geofence")
    app.register_blueprint(deviation_bp, url_prefix="/api/deviation")
    app.register_blueprint(source_bp, url_prefix="/api/source")
    app.register_blueprint(sync_bp, url_prefix="/api/sync")

    app.register_blueprint(
    presence_bp,
    url_prefix="/api/presence"
    )

    @app.get("/")
    def home():
        return {
            "message": "SMART BUS backend is running",
            "status": "success"
        }

    return app