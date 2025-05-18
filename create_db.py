import sqlite3
import os

os.makedirs('db', exist_ok=True)
conn = sqlite3.connect('db/tasks.db')

conn.execute('''
CREATE TABLE semesters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
''')

conn.execute('''
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL,
    week INTEGER NOT NULL,
    title TEXT NOT NULL,
    subject TEXT,
    deadline TEXT,
    description TEXT,
    is_done INTEGER DEFAULT 0,
    FOREIGN KEY (semester_id) REFERENCES semesters(id)
);
''')

conn.execute("INSERT INTO semesters (name) VALUES ('Семестр 1')")

conn.commit()
conn.close()

print("База данных создана!")
