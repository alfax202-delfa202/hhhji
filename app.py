from flask import Flask, request, jsonify, send_from_directory, session
import sqlite3, os, uuid, datetime

app = Flask(__name__)
app.secret_key = 'BAZZI_SECRET_99'

UPLOAD_FOLDER = 'public/uploads'
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

def get_db():
    conn = sqlite3.connect('bazziai_core.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, avatar TEXT DEFAULT "default.png")')
    conn.execute('CREATE TABLE IF NOT EXISTS roars (id TEXT PRIMARY KEY, username TEXT, content TEXT, media TEXT, type TEXT, time TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, roar_id TEXT, username TEXT, text TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS likes (roar_id TEXT, username TEXT, PRIMARY KEY(roar_id, username))')
    conn.commit()

@app.route('/')
def home(): return send_from_directory('public', 'index.html')

@app.route('/uploads/<path:filename>')
def get_file(filename): return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['user'], data['pass']))
        conn.commit()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "المستخدم موجود مسبقاً"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = get_db().execute("SELECT * FROM users WHERE username=? AND password=?", (data['user'], data['pass'])).fetchone()
    if user:
        session['user'] = user['username']
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "بيانات خاطئة"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return jsonify({"status": "success"})

@app.route('/check_auth')
def check_auth():
    if 'user' in session:
        user = get_db().execute("SELECT * FROM users WHERE username=?", (session['user'],)).fetchone()
        return jsonify({"logged": True, "user": dict(user)})
    return jsonify({"logged": False})

@app.route('/post_roar', methods=['POST'])
def post_roar():
    if 'user' not in session: return jsonify({"status": "error"})
    file = request.files.get('media')
    r_id = str(uuid.uuid4())[:8]
    m_name, m_type = "", "text"
    if file:
        m_name = f"{r_id}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, m_name))
        m_type = "video" if file.content_type.startswith('video') else "image"
    conn = get_db()
    conn.execute("INSERT INTO roars (id, username, content, media, type, time) VALUES (?, ?, ?, ?, ?, ?)",
                 (r_id, session['user'], request.form.get('content'), m_name, m_type, datetime.datetime.now()))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/get_roars')
def get_roars():
    conn = get_db()
    # جلب المنشورات مع التحقق من الإعجاب لكل منشور
    roars = conn.execute('''
        SELECT roars.*, users.avatar, 
        (SELECT COUNT(*) FROM likes WHERE roar_id = roars.id) as likes_count,
        (SELECT COUNT(*) FROM likes WHERE roar_id = roars.id AND username = ?) as liked
        FROM roars JOIN users ON roars.username = users.username 
        ORDER BY roars.time DESC
    ''', (session.get('user'),)).fetchall()
    return jsonify([dict(r) for r in roars])

@app.route('/toggle_like', methods=['POST'])
def toggle_like():
    if 'user' not in session: return jsonify({"status": "error"})
    roar_id = request.json.get('roar_id') or request.json.get('id')
    conn = get_db()
    liked = conn.execute("SELECT * FROM likes WHERE roar_id=? AND username=?", (roar_id, session['user'])).fetchone()
    if liked:
        conn.execute("DELETE FROM likes WHERE roar_id=? AND username=?", (roar_id, session['user']))
    else:
        conn.execute("INSERT INTO likes (roar_id, username) VALUES (?, ?)", (roar_id, session['user']))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user' not in session: return jsonify({"status": "error"})
    data = request.json
    conn = get_db()
    conn.execute("INSERT INTO comments (roar_id, username, text) VALUES (?, ?, ?)", (data['roar_id'], session['user'], data['text']))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/get_comments/<roar_id>')
def get_comments(roar_id):
    comments = get_db().execute("SELECT * FROM comments WHERE roar_id=?", (roar_id,)).fetchall()
    return jsonify([dict(c) for c in comments])

@app.route('/delete_roar/<roar_id>', methods=['DELETE'])
def delete_roar(roar_id):
    if 'user' not in session: return jsonify({"status": "error"})
    conn = get_db()
    conn.execute("DELETE FROM roars WHERE id=? AND username=?", (roar_id, session['user']))
    conn.commit()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(port=8080, host='0.0.0.0', debug=True)

