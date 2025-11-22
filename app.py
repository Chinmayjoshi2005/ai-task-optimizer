from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json
import os
from datetime import datetime
from tracker import AITaskOptimizer
from models import db, User, Task, Schedule
from forms import LoginForm, RegistrationForm, ProfileForm, TaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_optimizer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Helper function to get today's date
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# Routes for authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Routes for the web application
@app.route('/')
@login_required
def index():
    # Get user's tasks
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').all()
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    tasks_data = {
        'pending': pending_tasks,
        'completed': completed_tasks,
        'schedules': {str(schedule.date): schedule.schedule_data for schedule in schedules}
    }
    
    return render_template('index.html', profile=current_user, tasks=tasks_data)

@app.route('/profile')
@login_required
def profile():
    # Convert user object to dictionary for JSON serialization
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'name': current_user.name,
        'role': current_user.role,
        'schedule_days': current_user.schedule_days,
        'peak_energy': current_user.peak_energy,
        'study_preference': current_user.study_preference,
        'family_time': current_user.family_time,
        'workout_preference': current_user.workout_preference,
        'workout_impact': current_user.workout_impact,
        'main_goals': current_user.main_goals,
        'sleep_schedule': current_user.sleep_schedule,
        'weekly_schedule': current_user.weekly_schedule,
        'is_admin': current_user.is_admin,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None
    }
    return render_template('profile.html', profile=user_data)

@app.route('/tasks')
@login_required
def tasks():
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').all()
    
    tasks_data = {
        'pending': pending_tasks,
        'completed': completed_tasks,
        'schedules': {}
    }
    
    return render_template('tasks.html', tasks=tasks_data)

@app.route('/schedule')
@login_required
def schedule():
    today = get_today()
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    
    tasks_data = {
        'pending': [],
        'completed': [],
        'schedules': {str(schedule.date): schedule.schedule_data for schedule in schedules}
    }
    
    return render_template('schedule.html', tasks=tasks_data, today=today)

# API routes for profile
@app.route('/api/profile', methods=['GET', 'POST'])
@login_required
def api_profile():
    if request.method == 'POST':
        data = request.json
        
        # Update user profile
        current_user.name = data.get('name', current_user.name)
        current_user.role = data.get('role', current_user.role)
        current_user.schedule_days = data.get('schedule_days', current_user.schedule_days)
        current_user.peak_energy = data.get('peak_energy', current_user.peak_energy)
        current_user.study_preference = data.get('study_preference', current_user.study_preference)
        current_user.family_time = data.get('family_time', current_user.family_time)
        current_user.workout_preference = data.get('workout_preference', current_user.workout_preference)
        current_user.workout_impact = data.get('workout_impact', current_user.workout_impact)
        current_user.main_goals = data.get('main_goals', current_user.main_goals)
        current_user.sleep_schedule = data.get('sleep_schedule', current_user.sleep_schedule)
        current_user.weekly_schedule = data.get('weekly_schedule', current_user.weekly_schedule)
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Profile updated"})
    
    # Return current user profile
    profile_data = {
        'name': current_user.name,
        'role': current_user.role,
        'schedule_days': current_user.schedule_days,
        'peak_energy': current_user.peak_energy,
        'study_preference': current_user.study_preference,
        'family_time': current_user.family_time,
        'workout_preference': current_user.workout_preference,
        'workout_impact': current_user.workout_impact,
        'main_goals': current_user.main_goals,
        'sleep_schedule': current_user.sleep_schedule,
        'weekly_schedule': current_user.weekly_schedule
    }
    
    return jsonify(profile_data)

# API routes for tasks
@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    if request.method == 'POST':
        data = request.json
        if data.get('action') == 'add':
            task = Task(
                user_id=current_user.id,
                description=data.get('description'),
                priority=data.get('priority'),
                duration=data.get('duration'),
                type=data.get('type'),
                preferences=data.get('preferences'),
                status='pending'
            )
            db.session.add(task)
            db.session.commit()
            return jsonify({"status": "success", "message": "Task added"})
        elif data.get('action') == 'complete':
            task_id = data.get('id')
            task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
            if task:
                task.status = 'completed'
                task.completed_date = datetime.now()
                db.session.commit()
                return jsonify({"status": "success", "message": "Task completed"})
    else:
        # Get user's tasks
        pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
        completed_tasks = Task.query.filter_by(user_id=current_user.id, status='completed').all()
        
        tasks_data = {
            'pending': [
                {
                    'id': task.id,
                    'description': task.description,
                    'priority': task.priority,
                    'duration': task.duration,
                    'type': task.type,
                    'preferences': task.preferences,
                    'status': task.status,
                    'added_date': task.added_date.strftime("%Y-%m-%d") if task.added_date else None
                } for task in pending_tasks
            ],
            'completed': [
                {
                    'id': task.id,
                    'description': task.description,
                    'type': task.type,
                    'completed_date': task.completed_date.strftime("%Y-%m-%d") if task.completed_date else None
                } for task in completed_tasks
            ]
        }
        
        return jsonify(tasks_data)

# API routes for schedule
@app.route('/api/schedule', methods=['POST'])
@login_required
def api_schedule():
    data = request.json
    date_str = data.get('date', get_today())
    
    # Check if schedule already exists for this date
    existing_schedule = Schedule.query.filter_by(user_id=current_user.id, date=datetime.strptime(date_str, "%Y-%m-%d").date()).first()
    if existing_schedule:
        return jsonify(existing_schedule.schedule_data)
    
    # Check if user has any pending tasks
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
    
    if not pending_tasks:
        # Generate default schedule when no tasks exist
        schedule_data = {
            "schedule": [
                {
                    "time": "7:00 AM - 7:30 AM",
                    "task": "Morning routine & light stretching",
                    "reason": "Gentle start to energize your day",
                    "type": "health"
                },
                {
                    "time": "8:00 AM - 10:00 AM",
                    "task": "Personal development time",
                    "reason": "High energy time for learning and growth",
                    "type": "study"
                },
                {
                    "time": "10:00 AM - 10:15 AM",
                    "task": "Break",
                    "reason": "Short break to refresh your mind",
                    "type": "break"
                },
                {
                    "time": "10:15 AM - 12:00 PM",
                    "task": "Focused work session",
                    "reason": "Continued focus time for personal projects",
                    "type": "work"
                },
                {
                    "time": "1:00 PM - 2:00 PM",
                    "task": "Lunch break",
                    "reason": "Nourishment and rest",
                    "type": "personal"
                },
                {
                    "time": "2:00 PM - 4:00 PM",
                    "task": "Skill building or hobbies",
                    "reason": "Afternoon time for personal interests",
                    "type": "personal"
                },
                {
                    "time": "4:00 PM - 5:00 PM",
                    "task": "Family/Personal time",
                    "reason": "Dedicated time for family or personal activities",
                    "type": "family"
                },
                {
                    "time": "6:00 PM - 7:00 PM",
                    "task": "Physical activity",
                    "reason": "Evening movement for health and wellbeing",
                    "type": "health"
                },
                {
                    "time": "8:00 PM - 9:00 PM",
                    "task": "Review and plan for tomorrow",
                    "reason": "Reflect on the day and prepare for tomorrow",
                    "type": "personal"
                }
            ],
            "daily_summary": "Balanced day with personal development, health, and family time. No specific tasks were found, so a general productivity schedule was created.",
            "tips": ["Take 5-min breaks every hour", "Stay hydrated", "Maintain good posture while working"]
        }
    else:
        # Generate schedule based on user's actual tasks
        schedule_data = {
            "schedule": [
                {
                    "time": "7:00 AM - 7:30 AM",
                    "task": "Morning routine & light stretching",
                    "reason": "Gentle start, won't tire you out",
                    "type": "health"
                },
                {
                    "time": "8:00 AM - 10:00 AM",
                    "task": "Deep work session - " + pending_tasks[0].description if pending_tasks else "Focused work",
                    "reason": "High energy time for demanding tasks",
                    "type": pending_tasks[0].type if pending_tasks else "work"
                },
                {
                    "time": "10:00 AM - 10:15 AM",
                    "task": "Break",
                    "reason": "Short break to refresh your mind",
                    "type": "break"
                },
                {
                    "time": "10:15 AM - 12:00 PM",
                    "task": "Project work - " + (pending_tasks[1].description if len(pending_tasks) > 1 else "Additional tasks"),
                    "reason": "Continued focus time for complex tasks",
                    "type": pending_tasks[1].type if len(pending_tasks) > 1 else "work"
                },
                {
                    "time": "1:00 PM - 2:00 PM",
                    "task": "Lunch break",
                    "reason": "Nourishment and rest",
                    "type": "personal"
                },
                {
                    "time": "2:00 PM - 3:30 PM",
                    "task": "College/Work commitments",
                    "reason": "Scheduled college/work time",
                    "type": "college/work"
                },
                {
                    "time": "4:00 PM - 5:00 PM",
                    "task": "Family time",
                    "reason": "Dedicated family time as per your preferences",
                    "type": "family"
                },
                {
                    "time": "6:00 PM - 7:00 PM",
                    "task": "Workout session",
                    "reason": "Evening workout as per your preferences",
                    "type": "health"
                },
                {
                    "time": "8:00 PM - 9:00 PM",
                    "task": "Review and plan for tomorrow",
                    "reason": "Reflect on the day and prepare for tomorrow",
                    "type": "personal"
                }
            ],
            "daily_summary": "Balanced day with study, work, health, and family time. High-energy tasks scheduled during peak hours based on your pending tasks.",
            "tips": ["Take 5-min breaks every hour", "Stay hydrated", "Maintain good posture while working"]
        }
    
    # Save schedule to database
    new_schedule = Schedule(
        user_id=current_user.id,
        date=datetime.strptime(date_str, "%Y-%m-%d").date(),
        schedule_data=schedule_data
    )
    db.session.add(new_schedule)
    db.session.commit()
    
    return jsonify(schedule_data)

# Admin route
@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', is_admin=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
    
    app.run(debug=True, port=5007)