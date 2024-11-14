from flask import jsonify, request
from flask_mail import Message
from flask_login import login_user
from flask_jwt_extended import create_access_token
from datetime import timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User
import re
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Challenge, UserChallenge
from datetime import datetime

@app.route('/challenges', methods=['GET'])
@jwt_required()
def get_challenges():
    challenges = Challenge.query.all()
    return jsonify([{
        'id': c.id,
        'title': c.title,
        'description': c.description,
        'difficulty': c.difficulty,
        'status': c.status,
        'score': c.score
    } for c in challenges]), 200

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = db.session.query(
        User.username,
        db.func.count(UserChallenge.id).label('challenges_solved'),
        db.func.sum(Challenge.score).label('total_score')
    ).outerjoin(
        UserChallenge, User.id == UserChallenge.user_id
    ).outerjoin(
        Challenge, UserChallenge.challenge_id == Challenge.id
    ).group_by(User.id, User.username)\
    .order_by(db.desc('total_score'))\
    .all()

    return jsonify([{
        'username': username,
        'solvedChallenges': solved or 0,
        'score': score or 0
    } for username, solved, score in leaderboard]), 200

@app.route('/user-status', methods=['GET'])
@jwt_required()
def get_user_status():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    stats = db.session.query(
        db.func.count(UserChallenge.id).label('solved'),
        db.func.sum(Challenge.score).label('score')
    ).join(
        Challenge, UserChallenge.challenge_id == Challenge.id
    ).filter(
        UserChallenge.user_id == current_user_id,
        UserChallenge.completed == True
    ).first()

    return jsonify({
        'username': user.username,
        'solvedChallenges': stats[0] or 0,
        'score': stats[1] or 0
    }), 200

@app.route('/complete-challenge/<int:challenge_id>', methods=['POST'])
@jwt_required()
def complete_challenge(challenge_id):
    current_user_id = get_jwt_identity()
    
    existing = UserChallenge.query.filter_by(
        user_id=current_user_id,
        challenge_id=challenge_id,
        completed=True
    ).first()
    
    if existing:
        return jsonify({'message': 'Challenge already completed'}), 400

    challenge = Challenge.query.get(challenge_id)
    if not challenge:
        return jsonify({'message': 'Challenge not found'}), 404

    completion = UserChallenge(
        user_id=current_user_id,
        challenge_id=challenge_id,
        completed=True,
        completed_at=datetime.utcnow()
    )
    
    db.session.add(completion)
    db.session.commit()

    return jsonify({
        'message': 'Challenge completed successfully',
        'score': challenge.score
    }), 200
    
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'message': 'Missing required fields'}), 400

    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        return jsonify({'message': 'Invalid email format'}), 400

    # Check if username exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    # Check if email exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400

    try:
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'username': new_user.username,
            'redirect': 'https://ctftachyon-24.vercel.app/leaderboard'

        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating user'}), 500
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    # Generate JWT token
    access_token = create_access_token(
        identity=user.id,
        expires_delta=timedelta(days=1)
    )

    # Login user using Flask-Login
    login_user(user)

    return jsonify({
        'message': 'Login successful',
        'username': user.username,
        'access_token': access_token,
        'isLoggedIn': True,
        'redirect': 'https://ctftachyon-24.vercel.app/profile'
    }), 200
    
    
@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Get user's rank
    rank_subquery = db.session.query(
        User.id,
        db.func.dense_rank().over(
            order_by=db.desc(db.func.sum(Challenge.score))
        ).label('rank')
    ).join(
        UserChallenge, User.id == UserChallenge.user_id
    ).join(
        Challenge, UserChallenge.challenge_id == Challenge.id
    ).group_by(User.id).subquery()

    user_rank = db.session.query(
        rank_subquery.c.rank
    ).filter(
        rank_subquery.c.id == current_user_id
    ).scalar() or 0

    # Get user's stats
    stats = db.session.query(
        db.func.count(UserChallenge.id).label('solved'),
        db.func.sum(Challenge.score).label('points')
    ).join(
        Challenge, UserChallenge.challenge_id == Challenge.id
    ).filter(
        UserChallenge.user_id == current_user_id,
        UserChallenge.completed == True
    ).first()

    return jsonify({
        'username': user.username,
        'email': user.email,
        'challengesCompleted': stats[0] or 0,
        'points': stats[1] or 0,
        'rank': user_rank
    }), 200

@app.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    
    if 'email' in data:
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, data['email']):
            return jsonify({'message': 'Invalid email format'}), 400
            
        # Check if email is already taken by another user
        existing_user = User.query.filter(
            User.email == data['email'], 
            User.id != current_user_id
        ).first()
        if existing_user:
            return jsonify({'message': 'Email already registered'}), 400
            
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error updating profile'}), 500