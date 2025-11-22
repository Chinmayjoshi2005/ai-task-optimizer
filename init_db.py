from app import app, db, User

with app.app_context():
    db.create_all()
    
    # Create admin user if not exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Database initialized and admin user created')
    else:
        print('Admin user already exists')