from flask import Flask, render_template, request, redirect
import sqlite3

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

    # Calculate total time
    total_time = sum(row[2] for row in data)

    conn.close()

    return render_template("dashboard.html", data=data, total_time=total_time)


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