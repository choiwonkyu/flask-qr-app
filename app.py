from flask import Flask, render_template_string, request, redirect, url_for, abort, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 세션을 위한 시크릿 키 (아무 문자열로 바꾸셔도 됩니다)

# ─────────────── DB 초기화 ───────────────

def init_db():
    if not os.path.exists('branches.db'):
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

# ─────────────── DB 처리 함수 ───────────────

def get_branch_by_slug(slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, phone, chat_url FROM branches WHERE slug = ?', (slug,))
    branch = cursor.fetchone()
    conn.close()
    return branch

def add_branch(name, phone, chat_url, slug):
    conn = sqlite3.connect('branches.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO branches (name, phone, chat_url, slug)
        VALUES (?, ?, ?, ?)
    ''', (name, phone, chat_url, slug))
    conn.commit()
    conn.close()

# ─────────────── 지점 QR 전용 페이지 ───────────────

@app.route('/branch/<slug>')
def branch_page(slug):
    branch = get_branch_by_slug(slug)
    if branch:
        name, phone, chat_url = branch
        return render_template_string('''
            <h1>{{ name }}</h1>
            <p><a href="tel:{{ phone }}">📞 전화 연결하기</a></p>
            <p><a href="{{ chat_url }}" target="_blank">💬 채팅 상담 (네이버 톡톡)</a></p>
        ''', name=name, phone=phone, chat_url=chat_url)
    else:
        abort(404)

# ─────────────── 관리자 로그인 및 지점 추가 ───────────────

@app.route('/admin/add', methods=['GET', 'POST'])
def add_branch_page():
    if not session.get('logged_in'):
        if request.method == 'POST':
            password = request.form.get('password')
            if password == 'admin123':  # 원하는 비밀번호로 변경 가능
                session['logged_in'] = True
                return redirect(url_for('add_branch_page'))
            else:
                return '''
                    <h3>❌ 비밀번호가 틀렸습니다.</h3>
                    <a href="/admin/add">다시 시도</a>
                '''
        return '''
            <h2>🔐 관리자 로그인</h2>
            <form method="post">
                <p>비밀번호: <input type="password" name="password" required></p>
                <button type="submit">로그인</button>
            </form>
        '''

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        chat_url = request.form['chat_url']
        slug = request.form['slug']
        add_branch(name, phone, chat_url, slug)
        return redirect(url_for('branch_page', slug=slug))

    return render_template_string('''
        <h2>🛠 지점 추가</h2>
        <form method="post">
            <p>지점명: <input type="text" name="name" required></p>
            <p>전화번호: <input type="text" name="phone" required></p>
            <p>채팅 URL: <input type="text" name="chat_url" required></p>
            <p>슬러그 (영문): <input type="text" name="slug" required></p>
            <p><button type="submit">추가하기</button></p>
        </form>
        <p><a href="/admin/logout">🔓 로그아웃</a></p>
    ''')

# ─────────────── 로그아웃 ───────────────

@app.route('/admin/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('add_branch_page'))

# ─────────────── 홈 ───────────────

@app.route('/')
def home():
    return '''
        <h2>🏠 QR 전용 서비스</h2>
        <p><a href="/admin/add">[지점 추가 관리자 화면]</a></p>
        <p>지점 QR 주소 예시: <code>/branch/gangnam</code></p>
    '''

# ─────────────── 실행 ───────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
