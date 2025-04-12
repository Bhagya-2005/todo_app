from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
import datetime
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for matplotlib
import matplotlib.pyplot as plt

app = Flask(__name__)

# Initialize database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route - Display tasks
@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Add task route - Add a new task
@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (task_name, start_time) VALUES (?, ?)', 
                 (task_name, start_time))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Mark task as completed
@app.route('/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET end_time = ? WHERE id = ?', (end_time, task_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

# Data science analysis route
@app.route('/analysis')
def analysis():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE end_time IS NOT NULL').fetchall()
    conn.close()

    # Convert tasks data to Pandas DataFrame for analysis
    df = pd.DataFrame([dict(task) for task in tasks])

    if not df.empty:
        # Calculate duration for each task in minutes
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['duration'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60

        # Calculate basic statistics
        average_time = df['duration'].mean()
        completion_rate = len(df) / (df.shape[0]) * 100  # Completed vs total completed

        # Plotting
        plt.figure(figsize=(10, 5))
        plt.bar(df['task_name'], df['duration'])
        plt.title('Time Spent on Tasks')
        plt.xlabel('Task Name')
        plt.ylabel('Duration (minutes)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('static/plot.png')
        plt.close()
    else:
        average_time = 0
        completion_rate = 0

    return render_template('analysis.html', average_time=average_time, 
                           completion_rate=completion_rate)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
