#!/usr/bin/env python3
"""
Script to create test users with predictions and final results
for testing the scoring system and UI
"""

from app import app, db, User, Candidate, Prediction, Result
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_data():
    with app.app_context():
        # Get all candidates
        candidates = Candidate.query.all()
        if len(candidates) < 3:
            print("❌ Error: Need at least 3 candidates to create predictions")
            return
        
        print(f"✅ Found {len(candidates)} candidates")
        
        # Create test users
        test_users = [
            {'username': 'alice', 'password': 'alice'},
            {'username': 'bob', 'password': 'bob'},
            {'username': 'charlie', 'password': 'charlie'},
            {'username': 'diana', 'password': 'diana'},
            {'username': 'eve', 'password': 'eve'},
        ]
        
        created_users = []
        for user_data in test_users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if existing_user:
                print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
                created_users.append(existing_user)
                continue
            
            user = User(
                username=user_data['username'],
                password_hash=generate_password_hash(user_data['password']),
                is_admin=False
            )
            db.session.add(user)
            created_users.append(user)
            print(f"✅ Created user: {user_data['username']}")
        
        db.session.commit()
        print(f"✅ Created {len([u for u in created_users if u.id])} users")
        
        # Create predictions for each user
        # We'll use different combinations to test various scoring scenarios
        predictions_data = [
            # User 1: Perfect podium (should get 15 points)
            {'first': 0, 'second': 1, 'third': 2},
            # User 2: All correct candidates but wrong positions (should get 9 points: 3+3+3)
            {'first': 1, 'second': 0, 'third': 2},
            # User 3: Two correct positions, one wrong candidate (should get 10 points: 5+5+0)
            {'first': 0, 'second': 1, 'third': 3},
            # User 4: One correct position, two wrong (should get 5 points: 5+0+0)
            {'first': 0, 'second': 2, 'third': 3},
            # User 5: All wrong (should get 0 points)
            {'first': 3, 'second': 4, 'third': 5},
        ]
        
        # Select first 3 candidates as final winners (for testing)
        final_first = candidates[0]
        final_second = candidates[1]
        final_third = candidates[2]
        
        print(f"\n📋 Setting final results:")
        print(f"   1ère place: {final_first.name} ({final_first.region})")
        print(f"   2ème place: {final_second.name} ({final_second.region})")
        print(f"   3ème place: {final_third.name} ({final_third.region})")
        
        # Create predictions
        for i, user in enumerate(created_users):
            # Check if prediction already exists
            existing_prediction = Prediction.query.filter_by(user_id=user.id).first()
            if existing_prediction:
                print(f"⚠️  Prediction for '{user.username}' already exists, skipping...")
                continue
            
            pred_data = predictions_data[i % len(predictions_data)]
            
            # Get candidate indices (making sure we don't go out of bounds)
            first_idx = min(pred_data['first'], len(candidates) - 1)
            second_idx = min(pred_data['second'], len(candidates) - 1)
            third_idx = min(pred_data['third'], len(candidates) - 1)
            
            prediction = Prediction(
                user_id=user.id,
                first_place_id=candidates[first_idx].id,
                second_place_id=candidates[second_idx].id,
                third_place_id=candidates[third_idx].id
            )
            db.session.add(prediction)
            
            # Show what prediction was created
            print(f"✅ Created prediction for {user.username}:")
            print(f"   1ère: {candidates[first_idx].name}")
            print(f"   2ème: {candidates[second_idx].name}")
            print(f"   3ème: {candidates[third_idx].name}")
        
        db.session.commit()
        print(f"\n✅ Created predictions for {len(created_users)} users")
        
        # Create final results (if not already exists)
        existing_result = Result.query.filter_by(is_final=True).first()
        if existing_result:
            print(f"\n⚠️  Final results already exist, updating...")
            existing_result.first_place_id = final_first.id
            existing_result.second_place_id = final_second.id
            existing_result.third_place_id = final_third.id
            existing_result.is_final = True
        else:
            print(f"\n📊 Creating final results...")
            final_result = Result(
                first_place_id=final_first.id,
                second_place_id=final_second.id,
                third_place_id=final_third.id,
                is_final=True
            )
            db.session.add(final_result)
        
        db.session.commit()
        print(f"✅ Final results created/updated")
        
        # Calculate scores
        print(f"\n🔢 Calculating scores...")
        from app import calculate_scores
        calculate_scores()
        
        # Display results
        print(f"\n📊 Final Scores:")
        print("-" * 60)
        predictions_with_scores = Prediction.query.join(User).order_by(Prediction.score.desc(), User.username).all()
        for i, pred in enumerate(predictions_with_scores, 1):
            print(f"{i}. {pred.user.username}: {pred.score} pts")
            print(f"   Prédiction: {pred.first_place.name} | {pred.second_place.name} | {pred.third_place.name}")
        
        print("\n✅ Test data created successfully!")
        print("\n💡 You can now:")
        print("   - Log in with any test user (username = password)")
        print("   - Check the dashboard to see scores and rankings")
        print("   - Verify the scoring calculations")

if __name__ == '__main__':
    create_test_data()


