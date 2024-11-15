from flask import jsonify, request
from flask_mail import Message
from flask_login import login_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash
from app import app, db
from app.models import User, Challenge, UserChallenge
import re

@app.route('/submit-flag', methods=['POST'])
@jwt_required()
def submit_flag():
    data = request.get_json()
    challenge_id = data.get('challenge_id')
    flag = data.get('flag')

    if not challenge_id or not flag:
        return jsonify({'message': 'Challenge ID and flag are required.'}), 400

    user_id = get_jwt_identity()
    challenge = Challenge.query.get(challenge_id)

    if not challenge:
        return jsonify({'message': 'Challenge not found.'}), 404

    user_challenge = UserChallenge.query.filter_by(user_id=user_id, challenge_id=challenge_id).first()

    if user_challenge and user_challenge.completed:
        return jsonify({'message': 'Challenge already completed.'}), 200

    if user_challenge and user_challenge.submitted_flag == flag:
        return jsonify({'message': 'Flag already submitted.'}), 400

    if flag == challenge.flag:
        if not user_challenge:
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                completed=True,
                completed_at=datetime.utcnow(),
                submitted_flag=flag
            )
            db.session.add(user_challenge)
        else:
            user_challenge.completed = True
            user_challenge.completed_at = datetime.utcnow()
            user_challenge.submitted_flag = flag

        user = User.query.get(user_id)
        user.total_score += challenge.score

        db.session.commit()
        return jsonify({'message': 'Correct flag! Score updated.', 'score': user.total_score}), 200
    else:
        if not user_challenge:
            user_challenge = UserChallenge(
                user_id=user_id,
                challenge_id=challenge_id,
                submitted_flag=flag
            )
            db.session.add(user_challenge)
        else:
            user_challenge.submitted_flag = flag

        db.session.commit()
        return jsonify({'message': 'Incorrect flag. Try again!'}), 400

# Existing routes...

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