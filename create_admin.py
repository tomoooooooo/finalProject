from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create an admin user
    admin_user = User(
        username='Admin',
        email='admin@yahoo.ro',
        password=generate_password_hash('1234'),  # Hash the password
        role='admin'  # Set the role to 'admin'
    )

    # Add the user to the database
    db.session.add(admin_user)
    db.session.commit()

    print("Admin user created successfully!")