from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'gymdb'
}

# Initialize DB
def init_db():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Users table (admins/trainers/members login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role ENUM('admin','trainer','member') DEFAULT 'member'
        )
    ''')

    # Members table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INT,
            gender ENUM('Male','Female','Other'),
            membership_type VARCHAR(50),
            start_date DATE,
            end_date DATE
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------- LOGIN ---------------- #
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash("Login Successful", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials", "danger")
    return render_template('login.html')

# ---------------- REGISTER ---------------- #
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form.get('role', 'member')

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s,%s,%s)", (username, password, role))
            conn.commit()
            conn.close()
            flash("Registered Successfully", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash("Username already exists", "danger")

    return render_template('register.html')

# ---------------- DASHBOARD ---------------- #
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'], role=session['role'])

# ---------------- MANAGE MEMBERS ---------------- #
@app.route('/members', methods=['GET','POST'])
def members():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        membership_type = request.form['membership_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        cursor.execute('''INSERT INTO members (name, age, gender, membership_type, start_date, end_date) 
                          VALUES (%s,%s,%s,%s,%s,%s)''',
                          (name, age, gender, membership_type, start_date, end_date))
        conn.commit()
        flash("Member Added Successfully", "success")

    cursor.execute("SELECT * FROM members")
    all_members = cursor.fetchall()
    conn.close()

    return render_template('members.html', members=all_members)

# ---------------- LOGOUT ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
