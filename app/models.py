from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import jwt
from time import time
from datetime import datetime, timedelta

login = LoginManager()

class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Unlocked')
    score = db.Column(db.Integer, default=100)
    flag = db.Column(db.String(100))
    users = db.relationship('User', secondary='user_challenge', overlaps="challenges")

class UserChallenge(db.Model):
    __tablename__ = 'user_challenge'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'))
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    challenges = db.relationship('Challenge', secondary='user_challenge', overlaps="users")
    total_score = db.Column(db.Integer, default=0)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    reset_token = db.Column(db.String(128), unique=True)
    reset_token_expiration = db.Column(db.DateTime)

    def get_reset_token(self, expires_in=600):
        reset_token = jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            db.app.config['SECRET_KEY'],  # Changed from app.config to db.app.config
            algorithm='HS256'
        )
        self.reset_token = reset_token
        self.reset_token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return reset_token

    @staticmethod
    def verify_reset_token(token):
        try:
            id = jwt.decode(token, db.app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
            return User.query.get(id)
        except:
            return None
        
@login.user_loader
def load_user(id):
    return User.query.get(int(id))