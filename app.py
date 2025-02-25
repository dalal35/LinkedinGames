from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from dateutil import parser

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('times.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS times
                 (id INTEGER PRIMARY KEY, player TEXT, game TEXT, time REAL, date TEXT)''')
    conn.commit()
    conn.close()

# Call init_db() once when the app starts
init_db()  # This runs when the module is imported, suitable for Gunicorn

# Home page with form and leaderboard
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player = request.form['player']
        game = request.form['game']
        time = float(request.form['time'])
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        conn = sqlite3.connect('times.db')
        c = conn.cursor()
        c.execute('INSERT INTO times (player, game, time, date) VALUES (?, ?, ?, ?)',
                  (player, game, time, date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # Fetch leaderboard data
    conn = sqlite3.connect('times.db')
    c = conn.cursor()
    c.execute('SELECT player, game, MIN(time) as best_time FROM times GROUP BY player, game ORDER BY best_time')
    leaderboard = c.fetchall()

    # Fetch all entries for display
    c.execute('SELECT player, game, time, date FROM times ORDER BY date DESC')
    all_times = c.fetchall()

    # Calculate averages
    c.execute('SELECT player, AVG(time) FROM times GROUP BY player')
    averages = c.fetchall()
    conn.close()

    return render_template('index.html', leaderboard=leaderboard, all_times=all_times, averages=averages)

if __name__ == '__main__':
    app.run(debug=True)