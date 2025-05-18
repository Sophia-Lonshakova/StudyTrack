from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Подключение к базе
def get_db_connection():
    conn = sqlite3.connect('db/tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

# Главная страница — список семестров
@app.route('/')
def semester_list():
    conn = get_db_connection()
    semesters = conn.execute('SELECT * FROM semesters').fetchall()
    conn.close()
    return render_template('semesters.html', semesters=semesters)

# Добавление нового семестра
@app.route('/add-semester', methods=['POST'])
def add_semester():
    name = request.form['name']
    conn = get_db_connection()
    conn.execute('INSERT INTO semesters (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('semester_list'))

# Список 15 недель в выбранном семестре
@app.route('/semester/<int:semester_id>')
def week_list(semester_id):
    conn = get_db_connection()
    semester = conn.execute('SELECT * FROM semesters WHERE id = ?', (semester_id,)).fetchone()
    conn.close()

    if semester is None:
        return "Семестр не найден", 404

    weeks = list(range(1, 16))
    return render_template('weeks.html', semester=semester, weeks=weeks)

# Задачи конкретной недели
@app.route('/semester/<int:semester_id>/week/<int:week_num>')
def week_tasks(semester_id, week_num):
    conn = get_db_connection()
    semester = conn.execute('SELECT * FROM semesters WHERE id = ?', (semester_id,)).fetchone()
    tasks = conn.execute('''
        SELECT * FROM tasks
        WHERE semester_id = ? AND week = ?
    ''', (semester_id, week_num)).fetchall()
    conn.close()

    if semester is None:
        return "Семестр не найден", 404

    return render_template('week_tasks.html',
                           semester=semester,
                           week=week_num,
                           tasks=tasks)

# Добавление задачи в выбранную неделю семестра
@app.route('/add/<int:semester_id>/<int:week_num>', methods=['GET', 'POST'])
def add_task_to_week(semester_id, week_num):
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        deadline = request.form['deadline']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO tasks (semester_id, week, title, subject, deadline, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (semester_id, week_num, title, subject, deadline, description))
        conn.commit()
        conn.close()

        return redirect(url_for('week_tasks', semester_id=semester_id, week_num=week_num))

    return render_template('add_task.html',
                           semester_id=semester_id,
                           week=week_num)

# Отметить задачу как выполненную
@app.route('/complete/<int:id>', methods=['POST'])
def complete_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT semester_id, week FROM tasks WHERE id = ?', (id,)).fetchone()

    if task is None:
        conn.close()
        return "Задача не найдена", 404

    conn.execute('UPDATE tasks SET is_done = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('week_tasks', semester_id=task['semester_id'], week_num=task['week']))

# Удаление задачи
@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT semester_id, week FROM tasks WHERE id = ?', (id,)).fetchone()

    if task is None:
        conn.close()
        return "Задача не найдена", 404

    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('week_tasks', semester_id=task['semester_id'], week_num=task['week']))

# Редактирование задачи
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (id,)).fetchone()

    if not task:
        conn.close()
        return "Задача не найдена", 404

    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        deadline = request.form['deadline']
        description = request.form['description']

        conn.execute('''
            UPDATE tasks
            SET title = ?, subject = ?, deadline = ?, description = ?
            WHERE id = ?
        ''', (title, subject, deadline, description, id))
        conn.commit()
        conn.close()

        return redirect(url_for('week_tasks',
                                semester_id=task['semester_id'],
                                week_num=task['week']))

    rendered_page = render_template('edit.html', task=task)
    conn.close()
    return rendered_page

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)



