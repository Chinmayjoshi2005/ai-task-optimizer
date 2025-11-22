from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    role = SelectField('Role', choices=[('', 'Select Role'), ('student', 'Student'), ('working professional', 'Working Professional')], validators=[DataRequired()])
    schedule_days = IntegerField('Schedule Days Per Week', validators=[DataRequired(), NumberRange(min=0, max=7)])
    peak_energy = SelectField('Peak Energy Time', choices=[
        ('', 'Select Energy Level'),
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night')
    ], validators=[DataRequired()])
    study_preference = SelectField('Study Preference', choices=[
        ('', 'Select Preference'),
        ('silence', 'Silence'),
        ('background noise', 'Background Noise')
    ], validators=[DataRequired()])
    family_time = StringField('Family Time', validators=[DataRequired()])
    workout_preference = SelectField('Workout Preference', choices=[
        ('', 'Select Preference'),
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('flexible', 'Flexible')
    ], validators=[DataRequired()])
    workout_impact = SelectField('Workout Impact', choices=[
        ('', 'Select Impact'),
        ('energized', 'Energized'),
        ('tired', 'Tired')
    ], validators=[DataRequired()])
    bedtime = StringField('Bedtime', validators=[DataRequired()])
    wake_time = StringField('Wake Time', validators=[DataRequired()])
    main_goals = TextAreaField('Main Goals', validators=[DataRequired()])
    submit = SubmitField('Save Profile')

class TaskForm(FlaskForm):
    description = StringField('Task Description', validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('', 'Select Priority'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ], validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired()])
    type = SelectField('Task Type', choices=[
        ('', 'Select Type'),
        ('study', 'Study'),
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('health', 'Health'),
        ('family', 'Family')
    ], validators=[DataRequired()])
    preferences = StringField('Preferences')
    submit = SubmitField('Add Task')