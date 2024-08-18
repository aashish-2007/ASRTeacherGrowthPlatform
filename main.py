from flask import Flask, render_template, redirect, url_for, request, session, flash, send_from_directory
import os
import hashlib
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
USER_FILE = 'users.txt'
RESOURCE_FOLDER = 'resources'
RESOURCE_LOG = 'resource_log.txt'
ENROLLMENT_FILE = 'enrollments.txt'
USER_COURSES_FILE = 'user_courses.txt'
USER_WEBINARS_FILE = 'user_webinars.txt'

# Ensure the resources folder exists
if not os.path.exists(RESOURCE_FOLDER):
    os.makedirs(RESOURCE_FOLDER)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        users = {}
        for line in f:
            username, hashed_password = line.strip().split(':')
            users[username] = hashed_password
        return users

def save_user(username, password):
    with open(USER_FILE, 'a') as f:
        f.write(f"{username}:{hash_password(password)}\n")

def log_resource_upload(username, filename):
    with open(RESOURCE_LOG, 'a') as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{username}:{filename}:{timestamp}\n")

def load_resource_log():
    logs = []
    if not os.path.exists(RESOURCE_LOG):
        return logs
    with open(RESOURCE_LOG, 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 3:
                username, filename, timestamp = parts
                logs.append({'username': username, 'filename': filename, 'timestamp': timestamp})
            else:
                print(f"Skipping malformed line in resource log: {line.strip()}")
    return logs

def load_enrollments():
    if not os.path.exists(ENROLLMENT_FILE):
        return {}
    with open(ENROLLMENT_FILE, 'r') as f:
        enrollments = {}
        for line in f:
            username, course_or_webinar = line.strip().split(':')
            if username not in enrollments:
                enrollments[username] = []
            enrollments[username].append(course_or_webinar)
        return enrollments

def save_enrollment(username, course_or_webinar):
    with open(ENROLLMENT_FILE, 'a') as f:
        f.write(f"{username}:{course_or_webinar}\n")

def load_user_courses():
    if not os.path.exists(USER_COURSES_FILE):
        return []
    with open(USER_COURSES_FILE, 'r') as f:
        return [line.strip().split(':') for line in f]

def save_user_course(owner, title, description, schedule):
    with open(USER_COURSES_FILE, 'a') as f:
        f.write(f"{owner}:{title}:{description}:{schedule}\n")

def load_user_webinars():
    if not os.path.exists(USER_WEBINARS_FILE):
        return []
    with open(USER_WEBINARS_FILE, 'r') as f:
        return [line.strip().split(':') for line in f]

def save_user_webinar(owner, title, description, schedule):
    with open(USER_WEBINARS_FILE, 'a') as f:
        f.write(f"{owner}:{title}:{description}:{schedule}\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users:
            flash('Username already exists. Please choose another.')
        else:
            save_user(username, password)
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        users = load_users()
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials, please try again.')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'username' in session:
        if request.method == 'POST':
            course = request.form['course']
            save_enrollment(session['username'], course)
            flash(f'You have successfully registered for the course: {course}')
            return redirect(url_for('courses'))

        courses = [
            {'title': 'Advanced Teaching Techniques', 'description': 'Learn advanced methodologies for effective teaching.', 'schedule': '2024-09-01', 'instructor': 'Dr. John Doe'},
            {'title': 'Educational Technology', 'description': 'Explore the latest tools and technologies in education.', 'schedule': '2024-09-10', 'instructor': 'Ms. Jane Smith'},
            {'title': 'Student Engagement Strategies', 'description': 'Engage students in the classroom with proven strategies.', 'schedule': '2024-09-15', 'instructor': 'Mr. William Brown'},
        ]
        enrollments = load_enrollments().get(session['username'], [])
        user_courses = load_user_courses()
        return render_template('courses.html', username=session['username'], courses=courses, enrollments=enrollments, user_courses=user_courses)
    return redirect(url_for('login'))

@app.route('/webinars', methods=['GET', 'POST'])
def webinars():
    if 'username' in session:
        if request.method == 'POST':
            webinar = request.form['webinar']
            save_enrollment(session['username'], webinar)
            flash(f'You have successfully registered for the webinar: {webinar}')
            return redirect(url_for('webinars'))

        webinars = [
            {'title': 'Innovative Education Approaches', 'description': 'Discuss the future of education with top experts.', 'schedule': '2024-08-25', 'presenter': 'Prof. Michael Green'},
            {'title': 'AI in Education', 'description': 'Understand the role of AI in modern education.', 'schedule': '2024-08-30', 'presenter': 'Dr. Emily White'},
        ]
        enrollments = load_enrollments().get(session['username'], [])
        user_webinars = load_user_webinars()
        return render_template('webinars.html', username=session['username'], webinars=webinars, enrollments=enrollments, user_webinars=user_webinars)
    return redirect(url_for('login'))

@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    if 'username' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            schedule = request.form['schedule']
            save_user_course(session['username'], title, description, schedule)
            flash('Course created successfully!')
            return redirect(url_for('courses'))
        return render_template('create_course.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/create_webinar', methods=['GET', 'POST'])
def create_webinar():
    if 'username' in session:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            schedule = request.form['schedule']
            save_user_webinar(session['username'], title, description, schedule)
            flash('Webinar created successfully!')
            return redirect(url_for('webinars'))
        return render_template('create_webinar.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/resources', methods=['GET', 'POST'])
def resources():
    if 'username' in session:
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                filename = file.filename
                file.save(os.path.join(RESOURCE_FOLDER, filename))
                log_resource_upload(session['username'], filename)
                flash('File successfully uploaded')
                return redirect(url_for('resources'))

        resource_logs = load_resource_log()
        return render_template('resources.html', resource_logs=resource_logs, username=session['username'])
    return redirect(url_for('login'))

@app.route('/download/<filename>')
def download_file(filename):
    if 'username' in session:
        return send_from_directory(RESOURCE_FOLDER, filename)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
