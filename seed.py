# seed_challenges.py
from app import db, app
from app.models import Challenge

def seed_challenges():
    challenges = [
        Challenge(
            id=1,
            title='Challenge 1',
            description='Solve a basic SQL injection vulnerability.',
            difficulty='Easy',
            status='Unlocked',
            score=100,
            flag='youfoundtheflag739'
        ),
        Challenge(
            id=2,
            title='Challenge 2',
            description='Explore Cross-Site Scripting (XSS) in a form.',
            difficulty='Medium',
            status='Unlocked',
            score=200,
            flag='FLAG{pass#123}'
        ),
        Challenge(
            id=3,
            title='Challenge 3',
            description='Bypass authentication using CSRF techniques.',
            difficulty='Hard',
            status='Unlocked',
            score=300,
            flag='FLAG{chhin_tapak_dam_dam}'
        ),
    ]
    
    with app.app_context():

        db.session.add_all(challenges)
        db.session.commit()
        print("Challenges seeded successfully.")

if __name__ == "__main__":
    seed_challenges()