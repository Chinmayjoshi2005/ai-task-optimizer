from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime
from tracker import AITaskOptimizer

app = Flask(__name__)
optimizer = AITaskOptimizer()

# Helper function to get today's date
def get_today():
    return datetime.now().strftime("%Y-%m-%d")

# Routes for the web application
@app.route('/')
def index():
    return render_template('index.html', profile=optimizer.user_profile, tasks=optimizer.tasks)

@app.route('/profile')
def profile():
    return render_template('profile.html', profile=optimizer.user_profile)

@app.route('/tasks')
def tasks():
    return render_template('tasks.html', tasks=optimizer.tasks)

@app.route('/schedule')
def schedule():
    today = get_today()
    return render_template('schedule.html', tasks=optimizer.tasks, today=today)

@app.route('/api/profile', methods=['GET', 'POST'])
def api_profile():
    if request.method == 'POST':
        data = request.json
        optimizer.user_profile.update(data)
        optimizer.save_profile()
        return jsonify({"status": "success", "message": "Profile updated"})
    return jsonify(optimizer.user_profile)

@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if request.method == 'POST':
        data = request.json
        if data.get('action') == 'add':
            import uuid
            task = {
                "id": str(uuid.uuid4()),  # Add unique ID to each task
                "description": data.get('description'),
                "priority": data.get('priority'),
                "duration": data.get('duration'),
                "type": data.get('type'),
                "preferences": data.get('preferences'),
                "status": "pending",
                "added_date": datetime.now().strftime("%Y-%m-%d")
            }
            optimizer.tasks['pending'].append(task)
            optimizer.save_tasks()
            return jsonify({"status": "success", "message": "Task added"})
        elif data.get('action') == 'complete':
            task_index = data.get('index')
            if task_index is not None and 0 <= task_index < len(optimizer.tasks['pending']):
                completed_task = optimizer.tasks['pending'].pop(task_index)
                completed_task['status'] = 'completed'
                completed_task['completed_date'] = datetime.now().strftime("%Y-%m-%d")
                optimizer.tasks['completed'].append(completed_task)
                optimizer.save_tasks()
                return jsonify({"status": "success", "message": "Task completed"})
    return jsonify(optimizer.tasks)

@app.route('/api/schedule', methods=['POST'])
def api_schedule():
    data = request.json
    date_str = data.get('date', get_today())
    
    # Check if schedule already exists for this date
    if 'schedules' in optimizer.tasks and date_str in optimizer.tasks['schedules']:
        # Return existing schedule
        return jsonify(optimizer.tasks['schedules'][date_str])
    
    # Generate schedule (this would integrate with AI in the future)
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
                "task": "Deep work session - Coding practice",
                "reason": "High energy time for demanding tasks",
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
                "task": "Project work",
                "reason": "Continued focus time for complex tasks",
                "type": "work"
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
        "daily_summary": "Balanced day with study, work, health, and family time. High-energy tasks scheduled during peak hours.",
        "tips": ["Take 5-min breaks every hour", "Stay hydrated", "Maintain good posture while working"]
    }
    
    # Save schedule
    if 'schedules' not in optimizer.tasks:
        optimizer.tasks['schedules'] = {}
    optimizer.tasks['schedules'][date_str] = schedule_data
    optimizer.save_tasks()
    
    return jsonify(schedule_data)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
