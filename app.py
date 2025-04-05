from flask import Flask, request, redirect, render_template, url_for, session, abort
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션을 위한 비밀 키

DATABASE = 'branches.db'
ADMIN_PASSWORD = '1234'  # 관리자 비밀번호

# -------------------------------
# DB 연결
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------------
# DB 초기화 (최초 1회만 실행)
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

# -------------------------------
# 로그인 필요 데코레이터
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# -------------------------------
# 로그인 페이지
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('add_branch_page'))
        else:
            error = "❌ 비밀번호가 틀렸습니다."
    return render_template('login.html', error=error)

# -------------------------------
# 로그아웃
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# -------------------------------
# 지점 추가 함수
def add_branch(name, phone, chat_url, slug):
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO branches (name, phone, chat_url, slug)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, chat_url, slug))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False
    conn.close()
    return True

# -------------------------------
# 지점 조회
def get_branch_by_slug(slug):
    conn = get_db_connection()
    branch = conn.execute('SELECT * FROM branches WHERE slug = ?', (slug,)).fetchone()
    conn.close()
    return branch

# -------------------------------
# 전체 지점 목록
def get_all_branches():
    conn = get_db_connection()
    branches = conn.execute('SELECT * FROM branches').fetchall()
    conn.close()
    return branches

# -------------------------------
# 지점 삭제
@app.route('/admin/delete/<slug>', methods=['POST'])
@login_required
def delete_branch(slug):
    conn = get_db_connection()
    conn.execute('DELETE FROM branches WHERE slug = ?', (slug,))
    conn.commit()
    conn.close()
    return redirect(url_for('add_branch_page'))

# -------------------------------
# 지점 수정
@app.route('/admin/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_branch(slug):
    conn = get_db_connection()
    branch = conn.execute('SELECT * FROM branches WHERE slug = ?', (slug,)).fetchone()

    if not branch:
        return "지점을 찾을 수 없습니다.", 404

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        conn.execute('''
            UPDATE branches SET name = ?, phone = ?, chat_url = ? WHERE slug = ?
        ''', (name, phone, chat_url, slug))
        conn.commit()
        conn.close()
        return redirect(url_for('add_branch_page'))

    conn.close()
    return render_template('edit_branch.html', branch=branch)

# -------------------------------
# 관리자: 지점 추가 및 목록 보기
@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_branch_page():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        slug = request.form['slug']
        success = add_branch(name, phone, chat_url, slug)
        if not success:
            return "❌ 슬러그가 중복되었습니다. 다른 slug를 사용해주세요."

    branches = get_all_branches()
    return render_template('add_branch.html', branches=branches)

# -------------------------------
# 고객용: QR 링크 페이지
@app.route('/b/<slug>')
def branch_page(slug):
    branch = get_branch_by_slug(slug)
    if not branch:
        return "❌ 해당 지점이 존재하지 않습니다.", 404
    return render_template('branch_page.html', branch=branch)

# -------------------------------
# 앱 실행
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)



@app.route('/')
def index():
    return render_template('login.html')
