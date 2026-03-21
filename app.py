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
    return render_template("dashboard.html")


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


# if __name__ == "__main__":
#     app.run(debug=True)