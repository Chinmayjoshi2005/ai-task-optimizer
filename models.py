from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile data
    name = db.Column(db.String(100))
    role = db.Column(db.String(50))
    schedule_days = db.Column(db.Integer)
    peak_energy = db.Column(db.String(20))
    study_preference = db.Column(db.String(50))
    family_time = db.Column(db.String(50))
    workout_preference = db.Column(db.String(20))
    workout_impact = db.Column(db.String(20))
    main_goals = db.Column(db.Text)
    sleep_schedule = db.Column(db.JSON)
    weekly_schedule = db.Column(db.JSON)
    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='user', lazy=True)
    schedules = db.relationship('Schedule', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    preferences = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_date = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Task {self.description}>'

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    schedule_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Schedule {self.date}>'