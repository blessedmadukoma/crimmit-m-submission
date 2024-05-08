import feedparser
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from sqlalchemy.exc import IntegrityError
import hashlib
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rss.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
jwt = JWTManager(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, url):
        self.user_id = user_id
        self.url = url

# db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing username, email, or password'}), 400

    try:
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Username or email already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or user.password != hashlib.sha256(password.encode()).hexdigest():
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

@app.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    token = request.json['token']
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = data['username']
        token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = data['username']
        del users[username]
        return jsonify({'message': 'Account deleted successfully'})
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

@app.route('/add_feed', methods=['POST'])
@jwt_required()
def add_feed():
    current_user = get_jwt_identity()
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'message': 'Missing URL'}), 400

    try:
        new_feed = Feed(user_id=current_user['id'], url=url)
        db.session.add(new_feed)
        db.session.commit()
        return jsonify({'message': 'RSS feed added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/get_feeds', methods=['GET'])
@jwt_required()
def get_feeds():
    current_user = get_jwt_identity()
    feeds = Feed.query.filter_by(user_id=current_user['id']).all()
    return jsonify({'feeds': [feed.url for feed in feeds]}), 200

@app.route('/display_feeds', methods=['GET'])
@jwt_required()
def display_feeds():
    current_user = get_jwt_identity()
    feeds = Feed.query.filter_by(user_id=current_user['id']).all()
    rss_data = {}

    for feed in feeds:
        parsed_feed = feedparser.parse(feed.url)
        rss_data[feed.url] = parsed_feed.entries

    return jsonify({'rss_data': rss_data}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
