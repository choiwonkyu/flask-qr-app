from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# ===============================
# 로그인 페이지
# ===============================
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            return redirect(url_for('add_branch_page'))
        return "❌ 아이디 또는 비밀번호가 틀렸습니다."
    return render_template('login.html')

# ===============================
# 지점 추가 + 목록
# ===============================
@app.route('/admin/add', methods=['GET', 'POST'])
def add_branch_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        slug = request.form['slug']
        try:
            cur.execute("""
                INSERT INTO branches (name, phone, chat_url, slug)
                VALUES (%s, %s, %s, %s)
            """, (name, phone, chat_url, slug))
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return "❌ 이미 존재하는 슬러그입니다."

    cur.execute("SELECT * FROM branches ORDER BY id DESC")
    branches = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('add_branch.html', branches=branches)

# ===============================
# 지점 삭제
# ===============================
@app.route('/admin/delete/<slug>', methods=['POST'])
def delete_branch(slug):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM branches WHERE slug = %s", (slug,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('add_branch_page'))

# ===============================
# 지점 수정
# ===============================
@app.route('/admin/edit/<slug>', methods=['GET', 'POST'])
def edit_branch(slug):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        cur.execute("""
            UPDATE branches
            SET name = %s, phone = %s, chat_url = %s
            WHERE slug = %s
        """, (name, phone, chat_url, slug))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('add_branch_page'))

    cur.execute("SELECT * FROM branches WHERE slug = %s", (slug,))
    branch = cur.fetchone()
    cur.close()
    conn.close()

    if not branch:
        return "❌ 지점 정보를 찾을 수 없습니다.", 404

    return render_template('edit_branch.html', branch=branch)

# ===============================
# 지점 상세 페이지 (고객용)
# ===============================
@app.route('/b/<slug>')
def branch_page(slug):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, phone, chat_url FROM branches WHERE slug = %s", (slug,))
    branch = cur.fetchone()
    cur.close()
    conn.close()

    if not branch:
        return "❌ 지점 정보를 찾을 수 없습니다.", 404

    return render_template('branch_page.html', name=branch[0], phone=branch[1], chat_url=branch[2])

# ===============================
# 앱 실행
# ===============================
if __name__ == '__main__':
    app.run(debug=True)
