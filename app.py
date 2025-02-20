# from flask import Flask, g, render_template, request, jsonify, redirect, url_for
# from functools import wraps
# import random
# import string
# import jwt
# import datetime
# import logging
# from db import get_db, close_db
# from flask_cors import CORS

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# CORS(app)

# logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# @app.teardown_appcontext
# def close_db_wrapper(error):
#     close_db(error)

# def generate_token(user):
#     payload = {
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
#         'iat': datetime.datetime.utcnow(),
#         'sub': user['id'],
#         'role': user['role']
#     }
#     return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# def token_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         logger.info(f"Received token: {token}")
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 403
#         try:
#             token = token.split(" ")[1]  # Extract token after 'Bearer'
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#             g.user_id = data['sub']
#             g.user_role = data['role']
#             logger.info(f"Token decoded successfully: {data}")
#         except jwt.ExpiredSignatureError:
#             logger.warning("Token has expired!")
#             return jsonify({'message': 'Token has expired!'}), 403
#         except jwt.InvalidTokenError:
#             logger.warning("Invalid token!")
#             return jsonify({'message': 'Invalid token!'}), 403
#         return f(*args, **kwargs)
#     return decorated_function

# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if g.user_role != role:
#                 return jsonify({'message': 'Access denied!'}), 403
#             return f(*args, **kwargs)
#         return decorated_function
#     return decorator

# @app.route('/login', methods=['GET'])
# def login_page():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     try:
#         data = request.get_json()
#         username = data['username']
#         password = data['password']
#         logger.info(f"Login attempt for username: {username}")
#         db = get_db()
#         user_cur = db.execute('SELECT * FROM member WHERE id=?', [username])
#         user = user_cur.fetchone()
#         if user:
#             logger.info(f"User found: {user['id']}")
#         if user and user['password'] == password:
#             token = generate_token(user)
#             logger.info(f"Token generated for user: {username}, {token}")
#             return jsonify({'token': token})
#         logger.warning(f"Invalid credentials for username: {username}")
#         return jsonify({'success': False, 'message': 'Invalid credentials'})
#     except Exception as e:
#         logger.error(f"Error during login: {e}")
#         return jsonify({'success': False, 'message': 'An error occurred during login'})

# @app.route('/logout')
# def logout():
#     return redirect(url_for('login_page'))

# @app.route('/')
# def index():
#     return redirect(url_for('login_page'))

# @app.route('/members')
# @token_required
# def members():
#     role = g.user_role
#     username = g.user_id
#     return render_template('members.html', role=role, username=username)

# @app.route('/member', methods=['GET'])
# @token_required
# def get_members():
#     db = get_db()
#     members_cur = db.execute('SELECT id, name, email, level FROM member')
#     members = members_cur.fetchall()
#     members_dict = [{'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']} for member in members]
#     return jsonify({'members': members_dict})

# @app.route('/member/<string:member_id>', methods=['GET'])
# @token_required
# def get_member(member_id):
#     db = get_db()
#     member_cur = db.execute('SELECT id, name, email, level FROM member WHERE id=?', [member_id])
#     member = member_cur.fetchone()
#     if member is None:
#         return jsonify({'message': 'Member not found'}), 404
#     return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

# def generate_random_password():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# @app.route('/member', methods=['POST'])
# @token_required
# @role_required('admin')
# def add_member():
#     new_member = request.get_json()
#     id = new_member['id']
#     name = new_member['name']
#     email = new_member['email']
#     level = new_member['level']
#     role = new_member.get('role', 'employee')
#     password = generate_random_password()

#     db = get_db()
#     db.execute('INSERT INTO member(id, name, email, level, password, role) VALUES(?, ?, ?, ?, ?, ?)', [id, name, email, level, password, role])
#     db.commit()
#     return jsonify({'message': 'Member added successfully'})

# @app.route('/member/<string:member_id>', methods=['PUT', 'PATCH'])
# @token_required
# def edit_member(member_id):
#     username = g.user_id
#     db = get_db()
#     member_cur = db.execute('SELECT id FROM member WHERE id=?', [member_id])
#     member = member_cur.fetchone()
#     if member is None:
#         return jsonify({'message': 'Member not found'}), 404
#     if g.user_role != 'admin' and member['id'] != username:
#         return jsonify({'message': 'Access denied!'}), 403
#     updated_member = request.get_json()
#     name = updated_member['name']
#     email = updated_member['email']
#     level = updated_member['level']
#     db.execute('UPDATE member SET name=?, email=?, level=? WHERE id=?', [name, email, level, member_id])
#     db.commit()
#     updated_member_cur = db.execute('SELECT id, name, email, level FROM member WHERE id=?', [member_id])
#     updated_member = updated_member_cur.fetchone()
#     return jsonify({'member': {'id': updated_member['id'], 'name': updated_member['name'], 'email': updated_member['email'], 'level': updated_member['level']}})

# @app.route('/member/<string:member_id>', methods=['DELETE'])
# @token_required
# @role_required('admin')
# def delete_member(member_id):
#     db = get_db()
#     member_cur = db.execute('SELECT id FROM member WHERE id=?', [member_id])
#     member = member_cur.fetchone()
#     if member is None:
#         return jsonify({'message': 'Member not found'}), 404
#     db.execute('DELETE FROM member WHERE id=?', [member_id])
#     db.commit()
#     return jsonify({'message': 'Member deleted successfully'})

# if __name__ == '__main__':
#     app.run(debug=True)







from flask import Flask, g, render_template, request, jsonify, redirect, url_for
from functools import wraps
import random
import string
import jwt
import datetime
import logging
from db import get_db, close_db
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Enable CORS with Authorization header support
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Logging configuration
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Close DB connection after request
@app.teardown_appcontext
def close_db_wrapper(error):
    close_db(error)

# Generate JWT token
def generate_token(user):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'sub': user['id'],
        'role': user['role']
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

# Token verification decorator
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        logger.info(f"Received token: {token}")

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            if "Bearer " in token:
                token = token.split(" ")[1]  # Extract token after 'Bearer'

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user_id = data['sub']
            g.user_role = data['role']
            logger.info(f"Token decoded successfully: {data}")
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired!")
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            logger.warning("Invalid token!")
            return jsonify({'message': 'Invalid token!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Role-based access decorator
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.user_role != role:
                return jsonify({'message': 'Access denied!'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Login page route
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Login API route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        logger.info(f"Login attempt for username: {username}")

        db = get_db()
        user_cur = db.execute('SELECT * FROM member WHERE id=?', [username])
        user = user_cur.fetchone()

        if user and user['password'] == password:
            logger.info(f"User authenticated: {user['id']}")
            token = generate_token(user)
            return jsonify({'token': token})
        else:
            logger.warning(f"Invalid credentials for username: {username}")
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({'success': False, 'message': 'An error occurred during login'}), 500

# Logout route
@app.route('/logout')
def logout():
    return redirect(url_for('login_page'))

# Default route
@app.route('/')
def index():
    return redirect(url_for('login_page'))

# # Members page (protected route)
# @app.route('/members')
# @token_required
# def members():
#     role = g.user_role
#     username = g.user_id
#     return render_template('members.html', role=role, username=username)
@app.route('/members', methods=['GET', 'OPTIONS'])
@token_required
def members():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    role = g.user_role
    username = g.user_id
    return render_template('members.html', role=role, username=username)

# Get all members (protected route)
@app.route('/member', methods=['GET'])
@token_required
def get_members():
    db = get_db()
    members_cur = db.execute('SELECT id, name, email, level FROM member')
    members = members_cur.fetchall()
    members_dict = [{'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']} for member in members]
    return jsonify({'members': members_dict})

# Get specific member by ID
@app.route('/member/<string:member_id>', methods=['GET'])
@token_required
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('SELECT id, name, email, level FROM member WHERE id=?', [member_id])
    member = member_cur.fetchone()
    if member is None:
        return jsonify({'message': 'Member not found'}), 404
    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

# Generate random password for new members
def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Add a new member (admin only)
@app.route('/member', methods=['POST'])
@token_required
@role_required('admin')
def add_member():
    new_member = request.get_json()
    id = new_member['id']
    name = new_member['name']
    email = new_member['email']
    level = new_member['level']
    role = new_member.get('role', 'employee')
    password = generate_random_password()

    db = get_db()
    db.execute('INSERT INTO member(id, name, email, level, password, role) VALUES(?, ?, ?, ?, ?, ?)',[id, name, email, level, password, role])
    db.commit()
    return jsonify({'message': 'Member added successfully'})

# Edit existing member details
@app.route('/member/<string:member_id>', methods=['PUT', 'PATCH'])
@token_required
def edit_member(member_id):
    username = g.user_id
    db = get_db()
    member_cur = db.execute('SELECT id FROM member WHERE id=?', [member_id])
    member = member_cur.fetchone()

    if member is None:
        return jsonify({'message': 'Member not found'}), 404

    if g.user_role != 'admin' and member['id'] != username:
        return jsonify({'message': 'Access denied!'}), 403

    updated_member = request.get_json()
    name = updated_member['name']
    email = updated_member['email']
    level = updated_member['level']

    db.execute('UPDATE member SET name=?, email=?, level=? WHERE id=?',[name, email, level, member_id])
    db.commit()

    updated_member_cur = db.execute('SELECT id, name, email, level FROM member WHERE id=?', [member_id])
    updated_member = updated_member_cur.fetchone()

    return jsonify({'member': {'id': updated_member['id'], 'name': updated_member['name'], 'email': updated_member['email'], 'level': updated_member['level']}})

# Delete member (admin only)
@app.route('/member/<string:member_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_member(member_id):
    db = get_db()
    member_cur = db.execute('SELECT id FROM member WHERE id=?', [member_id])
    member = member_cur.fetchone()

    if member is None:
        return jsonify({'message': 'Member not found'}), 404

    db.execute('DELETE FROM member WHERE id=?', [member_id])
    db.commit()

    return jsonify({'message': 'Member deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
