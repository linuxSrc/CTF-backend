from app import app, db
from app.models import User, Challenge, UserChallenge
from sqlalchemy import text
import sys

def check_database():
    try:
        with app.app_context():
            # Test 1: Basic Connection
            result = db.session.execute(text('SELECT 1')).scalar()
            print("✓ Database connection successful")

            # Test 2: Check Tables
            tables = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).fetchall()
            print("\nExisting tables:")
            for table in tables:
                print(f"✓ {table[0]}")

            # Test 3: Count Records
            user_count = User.query.count()
            challenge_count = Challenge.query.count()
            completion_count = UserChallenge.query.count()

            print("\nRecord counts:")
            print(f"Users: {user_count}")
            print(f"Challenges: {challenge_count}")
            print(f"Challenge Completions: {completion_count}")

            return True

    except Exception as e:
        print(f"\n❌ Database Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_database()
    sys.exit(0 if success else 1)