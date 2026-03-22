from flask import Flask, render_template, request, redirect,session
import sqlite3
from datetime import datetime
from models.db import init_db
import os
init_db()
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.secret_key = "your_secret_key"

def get_db():
    return sqlite3.connect('database/database.db')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM study ORDER BY date DESC")
    data = cursor.fetchall()

    total_time = sum(row[2] for row in data)
    
    #  Prepare data for chart
    subjects = {}
    for row in data:
        subject = row[1]
        time = row[2]

        if subject in subjects:
            subjects[subject] += time
        else:
            subjects[subject] = time

    labels = list(subjects.keys())
    values = list(subjects.values())

    #  Streak logic
    dates = list(set(row[3][:10] for row in data))  # get unique dates
    dates.sort(reverse=True)

    streak = 0
    today = datetime.now().date()

    for i, d in enumerate(dates):
        d = datetime.strptime(d, "%Y-%m-%d").date()
        if (today - d).days == i:
            streak += 1
        else:
            break

    conn.close()
    productivity = min(100, total_time * 2) 
    if total_time < 60:
        suggestion = "Try to study at least 1 hour daily."
    elif total_time < 180:
        suggestion = "Good progress! Try increasing focus time."
    else:
        suggestion = "Excellent consistency! Keep it up 🔥"

    return render_template("dashboard.html",
                       data=data,
                       total_time=total_time,
                       labels=labels,
                       values=values,
                       productivity=productivity,
                       suggestion=suggestion)


@app.route('/add', methods=['POST'])
def add():
    subject = request.form['subject']
    time = request.form['time']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO study (subject, time) VALUES (?, ?)", (subject, time))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM study WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        subject = request.form['subject']
        time = request.form['time']

        cursor.execute("UPDATE study SET subject=?, time=? WHERE id=?",
                       (subject, time, id))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    cursor.execute("SELECT * FROM study WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()

    return render_template("edit.html", row=row)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                           (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect('/login')

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# if __name__ == "__main__":
#     app.run(debug=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))