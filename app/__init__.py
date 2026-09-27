
from flask import Flask

from app.config import Config
from app.extensions import db, jwt, bcrypt, cors


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    # Import all database models
    from app.models import (
        User,
        Student,
        Bus,
        Route,
        Trip,
        BoardingPoint,
        ParentStudentLink,
        GPSLocation,
        AttendanceRecord,
        Notification,
        SOSEvent,
    )
    from app.models.presence_event import PresenceEvent
    from app.models.network_event import NetworkEvent

    # Import existing blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.bus_routes import bus_bp
    from app.routes.student_routes import student_bp
    from app.routes.route_routes import route_bp
    from app.routes.trip_routes import trip_bp
    from app.routes.parent_routes import parent_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.sos_routes import sos_bp
    from app.routes.admin_routes import admin_bp

    from app.routes.gps_routes import gps_bp
    from app.routes.eta_routes import eta_bp
    from app.routes.live_routes import live_bp
    from app.routes.presence_routes import presence_bp
    from app.routes.network_routes import network_bp
    from app.routes.sync_routes import sync_bp
    from app.routes.passenger_routes import passenger_bp
    from app.routes.source_routes import source_bp
    from app.routes.geofence_routes import geofence_bp
    from app.routes.deviation_routes import deviation_bp
    from app.routes.notification_dispatch_routes import (
        notification_dispatch_bp,
    )

    # Register core blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(bus_bp, url_prefix="/api/buses")
    app.register_blueprint(student_bp, url_prefix="/api/students")
    app.register_blueprint(route_bp, url_prefix="/api/routes")
    app.register_blueprint(trip_bp, url_prefix="/api/trips")
    app.register_blueprint(parent_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(admin_bp)

    # Register additional feature blueprints
    app.register_blueprint(gps_bp, url_prefix="/api/gps")
    app.register_blueprint(eta_bp, url_prefix="/api/eta")
    app.register_blueprint(live_bp, url_prefix="/api/trips")
    app.register_blueprint(presence_bp, url_prefix="/api/presence")
    app.register_blueprint(network_bp, url_prefix="/api/network")
    app.register_blueprint(sync_bp, url_prefix="/api/sync")
    app.register_blueprint(passenger_bp, url_prefix="/api/trips")
    app.register_blueprint(source_bp, url_prefix="/api/source")
    app.register_blueprint(geofence_bp, url_prefix="/api/geofences")
    app.register_blueprint(deviation_bp, url_prefix="/api/deviation")
    app.register_blueprint(
        notification_dispatch_bp,
        url_prefix="/api/notifications",
    )

    @app.route("/")
    def home():
        return {
            "project": "SMART BUS",
            "status": "Backend running",
        }

    with app.app_context():
        db.create_all()

    return app