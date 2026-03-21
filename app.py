from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
app = Flask(__name__)

def get_db():
    return sqlite3.connect('database/database.db')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
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

    return render_template("dashboard.html",
                       data=data,
                       total_time=total_time,
                       labels=labels,
                       values=values)


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

# if __name__ == "__main__":
#     app.run(debug=True)