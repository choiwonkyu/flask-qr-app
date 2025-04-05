import sqlite3

def add_branch(name, phone, chat_url, slug):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO branches (name, phone, chat_url, slug)
                VALUES (?, ?, ?, ?)
            ''', (name, phone, chat_url, slug))
            conn.commit()
    except Exception as e:
        print("DB 오류:", e)