from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import sys

# Initialize extensions without binding to the app
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    jwt.init_app(app)
    
    CORS(app, resources={
        r"/*": {
            "origins": ["https://ctftachyon-24.vercel.app"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        # Only migrate up to the latest migration
        try:
            db.create_all()  # Optional: Remove if using only Flask-Migrate
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")

    from app import routes, models

    return app

app = create_app()