import sqlite3

# 데이터베이스 연결 (없으면 자동 생성됨)
conn = sqlite3.connect('branches.db')
cursor = conn.cursor()

# 지점 테이블 생성 SQL 실행
cursor.execute('''
CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    chat_url TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE
)
''')

conn.commit()
conn.close()

print("✅ 지점 테이블이 생성되었습니다.")
