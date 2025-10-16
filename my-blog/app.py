from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }

# 建表（第一次執行會建立資料庫與表格）
with app.app_context():
    db.create_all()

# ------------------------
# RESTful API (JSON)
# ------------------------

# GET /api/posts           -> list posts
@app.route('/api/posts', methods=['GET'])
def api_list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([p.to_dict() for p in posts])

# GET /api/posts/<id>      -> get one post
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    p = Post.query.get_or_404(post_id)
    return jsonify(p.to_dict())

# POST /api/posts          -> create post (expects JSON)
@app.route('/api/posts', methods=['POST'])
def api_create_post():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    title = data.get('title', '').strip()
    author = data.get('author', '').strip()
    content = data.get('content', '').strip()
    if not title or not author or not content:
        return jsonify({"error": "title/author/content are required"}), 400

    new_post = Post(title=title, author=author, content=content)
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

# PUT /api/posts/<id>      -> update post (expects JSON)
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
    p = Post.query.get_or_404(post_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    title = data.get('title', '').strip()
    author = data.get('author', '').strip()
    content = data.get('content', '').strip()
    if not title or not author or not content:
        return jsonify({"error": "title/author/content are required"}), 400

    p.title = title
    p.author = author
    p.content = content
    db.session.commit()
    return jsonify(p.to_dict())

# DELETE /api/posts/<id>   -> delete post
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    p = Post.query.get_or_404(post_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200

# ------------------------
# Frontend pages (Jinja templates)
# ------------------------

# Home: show posts list
@app.route('/')
def index():
    # 可以直接在模板裡 fetch API，但這裡也把 posts 傳過去以方便 server-render
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

# New post page (form)
@app.route('/new')
def new_post_page():
    return render_template('new.html')

# View single post page
@app.route('/post/<int:post_id>')
def show_post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Edit page
@app.route('/post/<int:post_id>/edit')
def edit_post_page(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('edit.html', post=post)

if __name__ == '__main__':
    app.run(debug=True)
