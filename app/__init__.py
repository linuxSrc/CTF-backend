from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
jwt = JWTManager(app)
CORS(app)

from app import routes, models

with app.app_context():
    db.create_all()
