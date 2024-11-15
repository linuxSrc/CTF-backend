from app import app, db
from app.models import Challenge, User

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if challenges exist
        if not Challenge.query.first():
            # Add initial challenges
            challenges = [
                Challenge(
                    title='Basic SQL Injection',
                    description='Find and exploit a basic SQL injection vulnerability.',
                    difficulty='Easy',
                    status='Unlocked',
                    score=100,
                    flag='CTF{sql_injection_basic}'
                ),
                Challenge(
                    title='XSS Challenge',
                    description='Identify and exploit a Cross-Site Scripting vulnerability.',
                    difficulty='Medium',
                    status='Unlocked',
                    score=200,
                    flag='CTF{xss_master}'
                )
            ]
            
            for challenge in challenges:
                db.session.add(challenge)
                
            db.session.commit()
            print("Database initialized with challenges!")

if __name__ == '__main__':
    init_db()