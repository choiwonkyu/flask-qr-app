from flask import Flask, request, redirect, render_template, url_for
import sqlite3

app = Flask(__name__)

# 비밀번호 설정
ADMIN_PASSWORD = "1234"

# -------------------------------
# DB 초기화 함수 (앱 실행 전에 수동 실행 필요)
def init_db():
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
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

# -------------------------------
# 지점 추가 함수
def add_branch(name, phone, chat_url, slug):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO branches (name, phone, chat_url, slug)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, chat_url, slug))
        conn.commit()
    except sqlite3.IntegrityError:
        # 이미 존재하는 slug일 때는 예외 처리
        conn.close()
        return False
    conn.close()
    return True

# -------------------------------
# 지점 정보 조회 함수
def get_branch_by_slug(slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM branches WHERE slug = ?', (slug,))
    branch = cursor.fetchone()
    conn.close()
    return branch

# -------------------------------
# 전체 지점 목록 조회 함수
def get_all_branches():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM branches')
    branches = cursor.fetchall()
    conn.close()
    return branches

# -------------------------------
# 지점 추가 페이지
@app.route('/admin/add', methods=['GET', 'POST'])
@requires_auth
def add_branch_page():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        slug = request.form['slug']
        success = add_branch(name, phone, chat_url, slug)
        if not success:
            return "❌ 이미 같은 슬러그가 존재합니다. 다른 슬러그를 입력해주세요."
    branches = get_all_branches()
    return render_template('add_branch.html', branches=branches)


# 지점 삭제 함수
def delete_branch(slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM branches WHERE slug = ?", (slug,))
    conn.commit()
    conn.close()

# 지점 정보 수정 함수
def update_branch(name, phone, chat_url, slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE branches SET name = ?, phone = ?, chat_url = ? WHERE slug = ?
    """, (name, phone, chat_url, slug))
    conn.commit()
    conn.close()

# 지점 삭제용 라우트
@app.route('/admin/delete/<slug>', methods=['POST'])
def delete_branch_route(slug):
    delete_branch(slug)
    return redirect(url_for('add_branch_page'))

# 지점 수정용 라우트
@app.route('/admin/edit/<slug>', methods=['GET', 'POST'])
def edit_branch(slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM branches WHERE slug = ?", (slug,))
    branch = cursor.fetchone()
    conn.close()

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

# -------------------------------
# 지점 목록 보기
@app.route('/admin/list')
def list_branches():
    branches = get_all_branches()
    return render_template('branch_list.html', branches=branches)

# -------------------------------
# QR로 접속한 고객이 보는 지점 페이지
@app.route('/b/<slug>')
def branch_page(slug):
    branch = get_branch_by_slug(slug)
    if not branch:
        return "❌ 지점 정보를 찾을 수 없습니다.", 404

    name, phone, chat_url = branch[1], branch[2], branch[3]
    return render_template('branch_page.html', name=name, phone=phone, chat_url=chat_url)

# -------------------------------
# 앱 실행
if __name__ == '__main__':
    app.run(debug=True)
