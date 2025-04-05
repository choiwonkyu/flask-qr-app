from flask import Flask, render_template, request, redirect, url_for, abort, Response
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
DATABASE = 'branches.db'
ADMIN_PASSWORD = "9876"  # 지점 수정/삭제시 사용

# ===============================
# 인증 (관리자 페이지 비밀번호 보호)
# ===============================
def check_auth(username, password):
    return username == 'admin' and password == '9876'  # 비번은 원하는 걸로 바꾸세요

def authenticate():
    return Response(
        '접근 권한이 없습니다.\n 브라우저에 사용자명과 비밀번호를 입력하세요.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# ===============================
# DB 연결
# ===============================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ===============================
# DB 초기화
# ===============================
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            chat_url TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ===============================
# 지점 관련 함수
# ===============================
def add_branch(name, phone, chat_url, slug):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO branches (name, phone, chat_url, slug)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, chat_url, slug))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise
    conn.close()

def get_all_branches():
    conn = get_db_connection()
    branches = conn.execute('SELECT * FROM branches').fetchall()
    conn.close()
    return branches

def get_branch_by_slug(slug):
    conn = get_db_connection()
    branch = conn.execute('SELECT * FROM branches WHERE slug = ?', (slug,)).fetchone()
    conn.close()
    return branch

def delete_branch(slug):
    conn = get_db_connection()
    conn.execute("DELETE FROM branches WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()

def update_branch(name, phone, chat_url, slug):
    conn = get_db_connection()
    conn.execute('''
        UPDATE branches SET name = ?, phone = ?, chat_url = ? WHERE slug = ?
    ''', (name, phone, chat_url, slug))
    conn.commit()
    conn.close()

# ===============================
# 관리자: 지점 추가 + 목록 보기
# ===============================
@app.route('/admin/add', methods=['GET', 'POST'])
@requires_auth
def add_branch_page():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        slug = request.form['slug']
        try:
            add_branch(name, phone, chat_url, slug)
            return redirect(url_for('add_branch_page'))
        except sqlite3.IntegrityError:
            return "❌ 이미 존재하는 slug입니다. 다른 이름을 사용해주세요.", 400
    branches = get_all_branches()
    return render_template('add_branch.html', branches=branches)

# 지점 삭제
@app.route('/admin/delete/<slug>', methods=['POST'])
@requires_auth
def delete_branch_route(slug):
    delete_branch(slug)
    return redirect(url_for('add_branch_page'))

# 지점 수정
@app.route('/admin/edit/<slug>', methods=['GET', 'POST'])
@requires_auth
def edit_branch(slug):
    branch = get_branch_by_slug(slug)
    if branch is None:
        return "존재하지 않는 지점입니다.", 404

    if request.method == 'POST':
        password = request.form.get('password')
        if password != ADMIN_PASSWORD:
            return "비밀번호가 틀렸습니다.", 403
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        update_branch(name, phone, chat_url, slug)
        return redirect(url_for('add_branch_page'))

    return render_template('edit_branch.html', branch=branch)

# ===============================
# 고객용: QR 접속
# ===============================
@app.route('/b/<slug>')
def branch_page(slug):
    branch = get_branch_by_slug(slug)
    if not branch:
        return "❌ 지점 정보를 찾을 수 없습니다.", 404
    return render_template('branch_page.html', branch=branch)

# ===============================
# 앱 실행
# ===============================
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
