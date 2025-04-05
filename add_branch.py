import sqlite3

def add_branch(name, phone, chat_url, slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO branches (name, phone, chat_url, slug)
        VALUES (?, ?, ?, ?)
    ''', (name, phone, chat_url, slug))
    conn.commit()
    conn.close()