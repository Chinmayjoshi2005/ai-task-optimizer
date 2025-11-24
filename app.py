from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import json
import os
from datetime import datetime, timedelta
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

# Serve favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'templates', 'image'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Helper function to get today's date
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# Helper methods for time calculations
def add_time(time_str, minutes):
    """Add minutes to time string and return new time string"""
    try:
        # Parse time string (e.g., "7:00 AM")
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            time_obj = datetime.strptime(time_str.strip(), "%I:%M %p")
        else:
            time_obj = datetime.strptime(time_str.strip(), "%H:%M")
        
        # Add minutes
        new_time = time_obj + timedelta(minutes=minutes)
        
        # Return in same format
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            return new_time.strftime("%I:%M %p").lstrip('0')
        else:
            return new_time.strftime("%H:%M")
    except:
        # Fallback to simple addition if parsing fails
        return time_str

def subtract_time(time_str, minutes):
    """Subtract minutes from time string and return new time string"""
    try:
        # Parse time string (e.g., "7:00 AM")
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            time_obj = datetime.strptime(time_str.strip(), "%I:%M %p")
        else:
            time_obj = datetime.strptime(time_str.strip(), "%H:%M")
        
        # Subtract minutes
        new_time = time_obj - timedelta(minutes=minutes)
        
        # Return in same format
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            result = new_time.strftime("%I:%M %p").lstrip('0')
            # Fix formatting issue with single digit hours
            if result.startswith(':'):
                result = '12' + result
            return result
        else:
            return new_time.strftime("%H:%M")
    except:
        # Fallback to simple subtraction if parsing fails
        return time_str

def parse_time_str(time_str):
    try:
        if "AM" in time_str.upper() or "PM" in time_str.upper():
            return datetime.strptime(time_str.strip(), "%I:%M %p")
        return datetime.strptime(time_str.strip(), "%H:%M")
    except:
        return datetime.strptime("7:00 AM", "%I:%M %p")

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

# AI optimize
@app.route('/api/ai_optimize', methods=['POST'])
@login_required
def api_ai_optimize():
    try:
        data = request.json or {}
        prompt = data.get('prompt', '').strip()
        date_str = data.get('date', get_today())

        pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
        if not pending_tasks:
            return jsonify({
                "error": "No tasks",
                "message": "AI needs tasks to optimize. Add tasks, then retry.",
                "requires_tasks": True
            }), 400

        try:
            sleep_schedule = json.loads(current_user.sleep_schedule) if isinstance(current_user.sleep_schedule, str) else (current_user.sleep_schedule or {})
        except Exception:
            sleep_schedule = {}
        wake_time = (sleep_schedule or {}).get('wake_time', '7:00 AM')
        bedtime = (sleep_schedule or {}).get('bedtime', '11:00 PM')

        # Simple prompt parsing to adjust blocks
        p = prompt.lower()
        wants_college = any(k in p for k in ["college", "class", "lecture"]) or (current_user.role and "student" in current_user.role)
        wants_exam = "exam" in p or "test" in p
        wants_morning_focus = "morning" in p and ("focus" in p or "deep" in p)
        # Extract time range like "7:00 AM to 5:30 PM"
        import re
        time_match = re.search(r"(\d{1,2}:\d{2}\s*(?:am|pm))\s*(?:to|-)\s*(\d{1,2}:\d{2}\s*(?:am|pm))", p, re.IGNORECASE)
        college_time_range = None
        if time_match:
            start_str = time_match.group(1).upper().replace('AM',' AM').replace('PM',' PM').replace('  ',' ')
            end_str = time_match.group(2).upper().replace('AM',' AM').replace('PM',' PM').replace('  ',' ')
            # Normalize and validate
            try:
                _ = datetime.strptime(start_str.strip(), "%I:%M %p")
                _ = datetime.strptime(end_str.strip(), "%I:%M %p")
                college_time_range = (start_str.strip(), end_str.strip())
            except Exception:
                college_time_range = None

        schedule_items = []

        def fmt(dt):
            return dt.strftime("%I:%M %p").lstrip('0')

        wake_dt = parse_time_str(wake_time)
        cursor = wake_dt

        morning_end_dt = cursor + timedelta(minutes=30)
        schedule_items.append({"time": f"{fmt(cursor)} - {fmt(morning_end_dt)}", "task": "Morning routine & light stretching", "reason": "Gentle start", "type": "health"})
        cursor = morning_end_dt

        he_target = wake_dt + timedelta(minutes=(60 if wants_morning_focus else 90))
        he_start_dt = max(cursor, he_target)
        he_end_dt = he_start_dt + timedelta(minutes=120)

        c_start_dt = None
        c_end_dt = None
        if college_time_range:
            c_start_dt = parse_time_str(college_time_range[0])
            c_end_dt = parse_time_str(college_time_range[1])

        if c_start_dt and he_start_dt < c_start_dt:
            if he_end_dt <= c_start_dt:
                schedule_items.append({"time": f"{fmt(he_start_dt)} - {fmt(he_end_dt)}", "task": f"Deep work - {pending_tasks[0].description}", "reason": "High-energy block aligned to your prompt", "type": pending_tasks[0].type})
                cursor = he_end_dt
            else:
                adj_end_dt = c_start_dt
                if (adj_end_dt - he_start_dt).total_seconds() >= 1800:
                    schedule_items.append({"time": f"{fmt(he_start_dt)} - {fmt(adj_end_dt)}", "task": f"Deep work - {pending_tasks[0].description}", "reason": "High-energy block aligned to your prompt", "type": pending_tasks[0].type})
                    cursor = adj_end_dt
        elif not c_start_dt:
            schedule_items.append({"time": f"{fmt(he_start_dt)} - {fmt(he_end_dt)}", "task": f"Deep work - {pending_tasks[0].description}", "reason": "High-energy block aligned to your prompt", "type": pending_tasks[0].type})
            cursor = he_end_dt

        if not c_start_dt or (cursor + timedelta(minutes=30)) <= c_start_dt:
            break_start_dt = cursor + timedelta(minutes=15)
            break_end_dt = break_start_dt + timedelta(minutes=15)
            schedule_items.append({"time": f"{fmt(break_start_dt)} - {fmt(break_end_dt)}", "task": "Break", "reason": "Short reset", "type": "break"})
            cursor = break_end_dt

        if c_start_dt:
            if cursor < c_start_dt:
                cursor = c_start_dt
            schedule_items.append({"time": f"{fmt(c_start_dt)} - {fmt(c_end_dt)}", "task": "College classes", "reason": "Prompt-specified college hours", "type": "college"})
            cursor = c_end_dt
        else:
            work_start_dt = cursor + timedelta(minutes=15)
            work_end_dt = work_start_dt + timedelta(minutes=90)
            task2 = f"Project work - {pending_tasks[1].description if len(pending_tasks) > 1 else 'Additional tasks'}"
            type2 = (pending_tasks[1].type if len(pending_tasks) > 1 else "work")
            schedule_items.append({"time": f"{fmt(work_start_dt)} - {fmt(work_end_dt)}", "task": task2, "reason": "Continued focus", "type": type2})
            cursor = work_end_dt

        lunch_start_dt = cursor + timedelta(minutes=60)
        lunch_end_dt = lunch_start_dt + timedelta(minutes=60)
        schedule_items.append({"time": f"{fmt(lunch_start_dt)} - {fmt(lunch_end_dt)}", "task": "Lunch break", "reason": "Nourishment", "type": "personal"})
        cursor = lunch_end_dt

        afternoon_start_dt = cursor + timedelta(minutes=60)
        afternoon_end_dt = afternoon_start_dt + timedelta(minutes=90)
        schedule_items.append({"time": f"{fmt(afternoon_start_dt)} - {fmt(afternoon_end_dt)}", "task": "College/Work commitments" if wants_college else "Task review & planning", "reason": "Aligned with prompt", "type": "college/work"})
        cursor = afternoon_end_dt

        # Family
        family_time = current_user.family_time or "6:00 PM - 7:00 PM"
        schedule_items.append({"time": family_time, "task": "Family time", "reason": "Preferences", "type": "family"})

        # Workout
        workout_pref = (current_user.workout_preference or "evening").lower()
        workout_time = "7:00 PM - 8:00 PM"
        if "morning" in workout_pref:
            workout_time = f"{add_time(wake_time, 30)} - {add_time(wake_time, 90)}"
        schedule_items.append({"time": workout_time, "task": "Workout session", "reason": f"{workout_pref.title()} workout", "type": "health"})

        # Evening review
        review_time_start = subtract_time(bedtime, 60)
        schedule_items.append({"time": f"{review_time_start} - {bedtime}", "task": "Review and plan for tomorrow", "reason": "Reflect and prepare", "type": "personal"})

        schedule_data = {
            "schedule": schedule_items,
            "daily_summary": f"Optimized using profile and {len(pending_tasks)} tasks. Prompt: {prompt}",
            "tips": [
                "Use high-energy blocks for deep work",
                "Take short breaks every hour",
                "Hydrate and move regularly"
            ]
        }

        # Save
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        existing = Schedule.query.filter_by(user_id=current_user.id, date=date_obj).first()
        if existing:
            existing.schedule_data = schedule_data
            db.session.commit()
        else:
            new_schedule = Schedule(user_id=current_user.id, date=date_obj, schedule_data=schedule_data)
            db.session.add(new_schedule)
            db.session.commit()
        return jsonify({"status": "success", "date": date_str, "schedule": schedule_data})
    except Exception as e:
        return jsonify({"error": "server_error", "message": f"Failed to optimize: {str(e)}"}), 500

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
    
    # Check if user has completed their profile
    if not current_user.name or not current_user.sleep_schedule:
        return jsonify({
            "error": "Profile incomplete",
            "message": "Please complete your profile before generating a schedule. We need your wake up and sleep times to create an optimized schedule."
        }), 400
    
    # Check if user has any pending tasks
    pending_tasks = Task.query.filter_by(user_id=current_user.id, status='pending').all()
    
    if not pending_tasks:
        return jsonify({
            "error": "No tasks",
            "message": "Please add some tasks before generating a schedule. The AI needs tasks to optimize your day."
        }), 400
    
    # Parse sleep schedule
    try:
        sleep_schedule = json.loads(current_user.sleep_schedule) if isinstance(current_user.sleep_schedule, str) else current_user.sleep_schedule
        wake_time = sleep_schedule.get('wake_time', '7:00 AM')
        bedtime = sleep_schedule.get('bedtime', '11:00 PM')
    except:
        wake_time = '7:00 AM'
        bedtime = '11:00 PM'
    
    # Generate schedule based on user's actual tasks and preferences
    schedule_items = []
    
    # Morning routine based on wake time
    morning_end = add_time(wake_time, 30)
    schedule_items.append({
        "time": f"{wake_time} - {morning_end}",
        "task": "Morning routine & light stretching",
        "reason": "Gentle start to energize your day based on your wake up time",
        "type": "health"
    })
    
    # High energy time for important tasks
    high_energy_start = add_time(wake_time, 60)  # 1 hour after waking
    high_energy_end = add_time(high_energy_start, 120)  # 2 hours block
    
    schedule_items.append({
        "time": f"{high_energy_start} - {high_energy_end}",
        "task": f"Deep work session - {pending_tasks[0].description}" if pending_tasks else "Focused work",
        "reason": "High energy time for demanding tasks based on your preferences",
        "type": pending_tasks[0].type if pending_tasks else "work"
    })
    
    # Break
    break_time_start = add_time(high_energy_end, 15)
    break_time_end = add_time(break_time_start, 15)
    
    schedule_items.append({
        "time": f"{break_time_start} - {break_time_end}",
        "task": "Break",
        "reason": "Short break to refresh your mind",
        "type": "break"
    })
    
    # Continue with tasks
    work_time_start = add_time(break_time_end, 15)
    work_time_end = add_time(work_time_start, 90)  # 1.5 hours
    
    schedule_items.append({
        "time": f"{work_time_start} - {work_time_end}",
        "task": f"Project work - {pending_tasks[1].description if len(pending_tasks) > 1 else 'Additional tasks'}",
        "reason": "Continued focus time for complex tasks",
        "type": pending_tasks[1].type if len(pending_tasks) > 1 else "work"
    })
    
    # Lunch break
    lunch_start = add_time(work_time_end, 60)
    lunch_end = add_time(lunch_start, 60)
    
    schedule_items.append({
        "time": f"{lunch_start} - {lunch_end}",
        "task": "Lunch break",
        "reason": "Nourishment and rest based on your schedule",
        "type": "personal"
    })
    
    # Afternoon work
    afternoon_start = add_time(lunch_end, 60)
    afternoon_end = add_time(afternoon_start, 90)
    
    schedule_items.append({
        "time": f"{afternoon_start} - {afternoon_end}",
        "task": "College/Work commitments",
        "reason": "Scheduled college/work time based on your weekly schedule",
        "type": "college/work"
    })
    
    # Family time
    family_time = current_user.family_time or "6:00 PM - 7:00 PM"
    schedule_items.append({
        "time": family_time,
        "task": "Family time",
        "reason": "Dedicated family time as per your preferences",
        "type": "family"
    })
    
    # Workout time based on user preference
    workout_pref = current_user.workout_preference or "evening"
    workout_time = "7:00 PM - 8:00 PM"  # Default evening
    if "morning" in workout_pref.lower():
        workout_time = f"{add_time(wake_time, 30)} - {add_time(wake_time, 90)}"
    
    schedule_items.append({
        "time": workout_time,
        "task": "Workout session",
        "reason": f"{workout_pref.capitalize()} workout as per your preferences",
        "type": "health"
    })
    
    # Evening review before bedtime
    review_time_start = subtract_time(bedtime, 60)
    schedule_items.append({
        "time": f"{review_time_start} - {bedtime}",
        "task": "Review and plan for tomorrow",
        "reason": "Reflect on the day and prepare for tomorrow based on your bedtime",
        "type": "personal"
    })
    
    # Create schedule data
    schedule_data = {
        "schedule": schedule_items,
        "daily_summary": f"Personalized schedule based on your wake time ({wake_time}), bedtime ({bedtime}), and {len(pending_tasks)} pending tasks.",
        "tips": [
            "Take 5-min breaks every hour",
            "Stay hydrated throughout the day",
            "Maintain good posture while working"
        ]
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
    
    app.run(debug=True, port=5012)
