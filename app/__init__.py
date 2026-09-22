from flask import Flask

from app.config import Config
from app.extensions import db, jwt, bcrypt, cors


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    # Import models so SQLAlchemy knows all tables
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
        SOSEvent
    )

    # Import and register routes
    from app.routes.auth_routes import auth_bp
    from app.routes.bus_routes import bus_bp
    from app.routes.student_routes import student_bp
    from app.routes.trip_routes import trip_bp
    from app.routes.parent_routes import parent_bp
    from app.routes.notification_routes import notification_bp
    from app.routes.sos_routes import sos_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(parent_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(sos_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def home():
        return {
            "project": "SMART BUS",
            "status": "Backend running"
        }

    # Create database tables
    with app.app_context():
        db.create_all()

    return app