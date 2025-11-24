import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class AITaskOptimizer:
    def __init__(self):
        self.profile_file = "user_profile.json"
        self.tasks_file = "tasks_data.json"
        self.user_profile = self.load_profile()
        self.tasks = self.load_tasks()
    
    def load_profile(self) -> Dict:
        """Load user profile from file or create new one"""
        if os.path.exists(self.profile_file):
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_profile(self):
        """Save user profile to file"""
        with open(self.profile_file, 'w') as f:
            json.dump(self.user_profile, f, indent=2)
    
    def load_tasks(self) -> Dict:
        """Load tasks from file"""
        if os.path.exists(self.tasks_file):
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return {"pending": [], "completed": [], "schedules": {}}
    
    def save_tasks(self):
        """Save tasks to file"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def setup_profile(self):
        """Interactive profile setup"""
        print("\n=== USER PROFILE SETUP ===")
        print("Let's understand your lifestyle to optimize your schedule!\n")
        
        # Basic info
        self.user_profile['name'] = input("Your name: ")
        self.user_profile['role'] = input("Are you a student or working professional? ")
        
        # College/Work schedule
        print("\n--- Weekly Schedule ---")
        college_days = input("How many days do you go to college/work per week? ")
        self.user_profile['schedule_days'] = int(college_days)
        
        schedule = {}
        for i in range(int(college_days)):
            day = input(f"Day {i+1} (e.g., Monday): ")
            start = input(f"  Start time for {day} (e.g., 9:00 AM): ")
            end = input(f"  End time for {day} (e.g., 5:00 PM): ")
            schedule[day] = {"start": start, "end": end, "type": "college/work"}
        
        self.user_profile['weekly_schedule'] = schedule
        
        # Energy and preferences
        print("\n--- Energy Patterns & Preferences ---")
        self.user_profile['peak_energy'] = input("When do you feel most energetic? (morning/afternoon/evening/night): ")
        self.user_profile['study_preference'] = input("Do you prefer studying in silence or with background noise? ")
        self.user_profile['sleep_schedule'] = {
            "bedtime": input("What time do you usually sleep? (e.g., 11:00 PM): "),
            "wake_time": input("What time do you wake up? (e.g., 7:00 AM): ")
        }
        
        # Constraints and priorities
        print("\n--- Personal Constraints ---")
        self.user_profile['family_time'] = input("What time do you prefer for family time? (e.g., 8-9 PM): ")
        self.user_profile['workout_preference'] = input("Do you prefer morning, evening, or flexible workout time? ")
        self.user_profile['workout_impact'] = input("Do workouts make you tired or energized? ")
        
        # Goals
        print("\n--- Goals & Priorities ---")
        self.user_profile['main_goals'] = input("What are your main goals? (e.g., improve grades, learn coding, stay healthy): ")
        
        self.save_profile()
        print("\n✓ Profile saved successfully!\n")
    
    def add_tasks(self):
        """Add tasks for optimization"""
        print("\n=== ADD TASKS ===")
        print("Enter your tasks (type 'done' when finished)\n")
        
        import uuid
        
        tasks = []
        while True:
            task_desc = input("Task: ")
            if task_desc.lower() == 'done':
                break
            
            # Get task details
            priority = input("  Priority (high/medium/low): ")
            duration = input("  Estimated duration (e.g., 1h, 30m): ")
            task_type = input("  Type (study/work/personal/health/family): ")
            preferences = input("  Any preferences? (e.g., needs silence, outdoors, flexible): ")
            
            task = {
                "id": str(uuid.uuid4()),  # Add unique ID to each task
                "description": task_desc,
                "priority": priority,
                "duration": duration,
                "type": task_type,
                "preferences": preferences,
                "status": "pending",
                "added_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            tasks.append(task)
            # Fixed: Only add the current task, not all tasks in the list
            self.tasks['pending'].append(task)
        
        self.save_tasks()
        print(f"\n✓ Added {len(tasks)} tasks!\n")
    
    def generate_ai_prompt(self, date_str: str) -> str:
        """Generate prompt for AI optimization"""
        prompt = f"""You are an intelligent task scheduler helping optimize someone's day.

USER PROFILE:
- Name: {self.user_profile.get('name', 'User')}
- Role: {self.user_profile.get('role', 'Student')}
- Peak Energy: {self.user_profile.get('peak_energy', 'Not specified')}
- Study Preference: {self.user_profile.get('study_preference', 'Not specified')}
- Sleep Schedule: {self.user_profile.get('sleep_schedule', {})}
- Family Time: {self.user_profile.get('family_time', 'Not specified')}
- Workout Preference: {self.user_profile.get('workout_preference', 'Not specified')}
- Workout Impact: {self.user_profile.get('workout_impact', 'Not specified')}
- Weekly Schedule: {json.dumps(self.user_profile.get('weekly_schedule', {}), indent=2)}
- Main Goals: {self.user_profile.get('main_goals', 'Not specified')}

TODAY'S PENDING TASKS:
{json.dumps(self.tasks.get('pending', []), indent=2)}

DATE: {date_str}

Please create an optimized daily schedule considering:
1. User's energy patterns (schedule demanding tasks during peak energy)
2. Study preferences (silence requirements, environment)
3. Workout timing (avoid scheduling after if it causes tiredness)
4. Family time constraints
5. Task priorities and deadlines
6. Realistic time blocks with breaks
7. College/work schedule if today is a college day

Create a schedule with:
- Specific time slots (e.g., 7:00 AM - 7:30 AM)
- Clear, actionable tasks
- Why each task is scheduled at that time
- Breaks and buffer time
- Balance between productivity and wellbeing

Format as JSON:
{{
  "schedule": [
    {{
      "time": "7:00 AM - 7:30 AM",
      "task": "Morning workout - Light cardio",
      "reason": "Scheduled early to energize the day, not too intense to avoid tiredness",
      "type": "health"
    }}
  ],
  "daily_summary": "Brief overview of the day's plan",
  "tips": ["Tip 1", "Tip 2"]
}}
"""
        return prompt
    
    def optimize_schedule(self, date_str: str = None):
        """Generate optimized schedule using AI logic"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Check if profile exists and complete
        required_profile_keys = ['name', 'role', 'peak_energy', 'study_preference', 
                                 'sleep_schedule', 'family_time', 'workout_preference', 
                                 'workout_impact', 'main_goals', 'weekly_schedule']
        
        if not self.user_profile or not all(k in self.user_profile and self.user_profile[k] for k in required_profile_keys):
            return {
                "error": "Profile incomplete",
                "message": "Please complete your profile before generating an optimized schedule."
            }
        
        if not self.tasks.get('pending'):
            return {
                "error": "No tasks",
                "message": "Please add some pending tasks before generating an optimized schedule."
            }
        
        # Here you would call the AI API (Claude/OpenAI)
        # For now, I'll show the prompt that would be sent
        prompt = self.generate_ai_prompt(date_str)
        
        print("=" * 60)
        print("AI OPTIMIZATION PROMPT (This would be sent to Claude API):")
        print("=" * 60)
        print(prompt)
        print("=" * 60)
        
        # Simulated AI response (you'll replace this with actual API call)
        print("\n📝 To use AI optimization:")
        print("1. Get an Anthropic API key from console.anthropic.com")
        print("2. Install: pip install anthropic")
        print("3. The system will send the above prompt to Claude")
        print("4. Claude will return an optimized schedule\n")
        
        # Example optimized schedule structure
        example_schedule = {
            "schedule": [
                {
                    "time": "7:00 AM - 7:30 AM",
                    "task": "Morning routine & light stretching",
                    "reason": "Gentle start, won't tire you out",
                    "type": "health"
                },
                {
                    "time": "9:00 AM - 1:00 PM",
                    "task": "College classes",
                    "reason": "Scheduled college day",
                    "type": "college"
                }
            ],
            "daily_summary": "Balanced day with study, health, and family time",
            "tips": ["Take 5-min breaks every hour", "Stay hydrated"]
        }
        
        return example_schedule
    
    def view_schedule(self, date_str: str = None):
        """View optimized schedule for a date"""
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        schedules = self.tasks.get('schedules', {})
        
        if date_str in schedules:
            schedule = schedules[date_str]
            print(f"\n=== SCHEDULE FOR {date_str} ===\n")
            
            for item in schedule.get('schedule', []):
                print(f"⏰ {item['time']}")
                print(f"   📌 {item['task']}")
                print(f"   💡 {item['reason']}\n")
            
            print(f"📊 Summary: {schedule.get('daily_summary', 'N/A')}")
            print("\n✨ Tips:")
            for tip in schedule.get('tips', []):
                print(f"   - {tip}")
        else:
            print(f"\n⚠ No schedule found for {date_str}")
            print("Generate one using option 3!\n")
    
    def show_profile(self):
        """Display current user profile"""
        if not self.user_profile:
            print("\n⚠ No profile found. Please set up your profile first!\n")
            return
        
        print("\n=== YOUR PROFILE ===\n")
        print(json.dumps(self.user_profile, indent=2))
        print()
    
    def show_tasks(self):
        """Display all tasks"""
        print("\n=== YOUR TASKS ===\n")
        
        pending = self.tasks.get('pending', [])
        completed = self.tasks.get('completed', [])
        
        print(f"📋 Pending Tasks ({len(pending)}):")
        for i, task in enumerate(pending, 1):
            print(f"{i}. {task['description']} - Priority: {task['priority']} - Duration: {task['duration']}")
        
        print(f"\n✅ Completed Tasks ({len(completed)}):")
        for i, task in enumerate(completed, 1):
            print(f"{i}. {task['description']}")
        print()
    
    def run(self):
        """Main application loop"""
        print("\n" + "="*60)
        print("    🎯 AI DAILY TASK OPTIMIZER")
        print("    Smart Scheduling for Students & Professionals")
        print("="*60)
        
        while True:
            print("\n--- MENU ---")
            print("1. Setup/Update Profile")
            print("2. Add Tasks")
            print("3. Generate Optimized Schedule")
            print("4. View Today's Schedule")
            print("5. View All Tasks")
            print("6. Show Profile")
            print("7. Exit")
            
            choice = input("\nSelect option (1-7): ")
            
            if choice == '1':
                self.setup_profile()
            elif choice == '2':
                self.add_tasks()
            elif choice == '3':
                date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d")
                self.optimize_schedule(date)
            elif choice == '4':
                self.view_schedule()
            elif choice == '5':
                self.show_tasks()
            elif choice == '6':
                self.show_profile()
            elif choice == '7':
                print("\n👋 Goodbye! Stay productive!\n")
                break
            else:
                print("\n⚠ Invalid option. Please try again.\n")

# Run the application
if __name__ == "__main__":
    app = AITaskOptimizer()
    app.run()