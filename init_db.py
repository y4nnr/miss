from app import app, db, User
from werkzeug.security import generate_password_hash

def init_users():
    """Initialize database with default users"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # List of regular users (password = username)
        users = ['yann']
        
        for username in users:
            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                user = User(
                    username=username,
                    password_hash=generate_password_hash(username),  # password = username
                    is_admin=False
                )
                db.session.add(user)
                print(f"Created user: {username}")
            else:
                # Update existing user to ensure is_admin is set
                existing_user.is_admin = False
                print(f"User {username} already exists")
        
        # Create admin user
        admin_username = 'admin'
        admin_user = User.query.filter_by(username=admin_username).first()
        if not admin_user:
            admin_user = User(
                username=admin_username,
                password_hash=generate_password_hash('admin'),  # password = admin
                is_admin=True
            )
            db.session.add(admin_user)
            print(f"Created admin user: {admin_username} (password: admin)")
        else:
            # Ensure admin user has admin privileges
            admin_user.is_admin = True
            print(f"Admin user {admin_username} already exists")
        
        db.session.commit()
        print("Database initialized successfully!")
        print(f"Admin credentials: username='admin', password='admin'")

if __name__ == '__main__':
    init_users()

