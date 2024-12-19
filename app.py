import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, Text, text, DateTime
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from flask import send_file
from io import BytesIO
from PIL import Image
from sqlalchemy import func


app = Flask(__name__, template_folder='C:/Users/arien/OneDrive/Рабочий стол/Курсач удач/FIZORGER_HTML-main/templates', static_folder='C:/Users/arien/OneDrive/Рабочий стол/Курсач удач/FIZORGER_HTML-main/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://arien:12345678@fizorger?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SECRET_KEY'] = 'dde8a6ba4fdf7dbecb55874b5c03d02fd575d5ad4623e70c'

db = SQLAlchemy(app)


logging.basicConfig(level=logging.DEBUG)
logging.debug(f"SECRET_KEY configured: {app.config['SECRET_KEY']}")

class User(db.Model):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    roleID = Column(Integer, nullable=False)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    patronymic = Column(String(50), nullable=True)
    login = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    genderID = Column(Integer, ForeignKey('Gender.id'), nullable=True)
    groupID = Column(Integer, ForeignKey('Group.id'), nullable=True)
    image = Column(LargeBinary, nullable=True)

    gender = relationship('Gender', back_populates='users')
    group = relationship('Group', back_populates='users')

class Gender(db.Model):
    __tablename__ = 'Gender'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    users = relationship('User', back_populates='gender')

class Group(db.Model):
    __tablename__ = 'Group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    users = relationship('User', back_populates='group')

class News(db.Model):
    __tablename__ = 'News'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    image = Column(LargeBinary, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

def update_user_password(login, plain_password):
    with app.app_context():
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')
        logging.debug(f"Generated password hash: {hashed_password}")
        user = db.session.execute(db.select(User).filter_by(login=login)).scalar_one_or_none()
        if user:
            user.password = hashed_password
            logging.debug(f"Updating password for user {user.login} to {hashed_password}")
            db.session.commit()
            logging.debug(f"Password updated for user {user.login}: {hashed_password}")
        else:
            logging.debug("User not found")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/media')
def media():
    return render_template('media.html')

@app.route('/media_video')
def media_video():
    return render_template('media_video.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/measure')
def measure():
    return render_template('measure.html')

@app.route('/measure_upcoming')
def measure_upcoming():
    return render_template('measure_upcoming.html')

@app.route('/measure_past')
def measure_past():
    return render_template('measure_past.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_login = request.form['login']
        user_password = request.form['password']
        user = db.session.execute(db.select(User).filter_by(login=user_login)).scalar_one_or_none()
        logging.debug(f"User found: {user}")
        if user:
            logging.debug(f"User password hash: {user.password}")
            logging.debug(f"Input password: {user_password}")
            if check_password_hash(user.password, user_password):
                session['user_id'] = user.id
                logging.debug(f"User {user_login} logged in successfully. User ID: {user.id}")
                logging.debug(f"Session before redirection: {session}")
                return redirect(url_for('user_panel'))
            else:
                flash('Неверный логин или пароль', 'error')
                logging.debug(f"Password check failed for user {user_login}")
        else:
            flash('Неверный логин или пароль', 'error')
            logging.debug(f"User {user_login} not found")
    return render_template('login.html')

@app.route('/user_panel')
def user_panel():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            if user.roleID == 1:  # Администратор
                return render_template('user_panel.html', user=user)
            elif user.roleID == 2:  # Физорг
                return render_template('physorg_panel.html', user=user)
            else:
                return redirect(url_for('login'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/check_session')
def check_session():
    user_id = session.get('user_id')
    if user_id:
        return f"User ID in session: {user_id}"
    else:
        return "No user ID in session"

@app.route('/check_db')
def check_db():
    try:
        result = db.session.execute(text('SELECT 1')).fetchone()
        if result:
            return "Подключение к базе данных успешно!"
        else:
            return "Не удалось подключиться к базе данных."
    except Exception as e:
        return f"Ошибка при подключении к базе данных: {e}"

@app.route('/check_user')
def check_user():
    user_login = 'admin'
    user = db.session.execute(db.select(User).filter_by(login=user_login)).scalar_one_or_none()
    if user:
        return f"User found: {user.login}, Password hash: {user.password}"
    else:
        return "User not found"

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user_login = data.get('login')
    user_password = data.get('password')
    logging.debug(f"Received login data: {data}")
    user = db.session.execute(db.select(User).filter_by(login=user_login)).scalar_one_or_none()
    logging.debug(f"User found: {user}")
    if user:
        logging.debug(f"User password hash: {user.password}")
        logging.debug(f"Input password: {user_password}")
        if check_password_hash(user.password, user_password):
            session['user_id'] = user.id
            logging.debug(f"User {user_login} logged in successfully. User ID: {user.id}")
            logging.debug(f"Session before redirection: {session}")
            return jsonify({"success": True, "message": "Login successful"}), 200
        else:
            logging.debug(f"Password check failed for user {user_login}")
            return jsonify({"success": False, "message": "Invalid login or password"}), 401
    else:
        logging.debug(f"User {user_login} not found")
        return jsonify({"success": False, "message": "Invalid login or password"}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({"success": True, "message": "Logout successful"}), 200

@app.route('/api/user_data', methods=['GET'])
def get_user_data_route():
    try:
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                user_data = {
                    'surname': user.surname,
                    'name': user.name,
                    'patronymic': user.patronymic,
                    'login': user.login,
                    'gender': user.genderID,
                    'group': user.groupID
                }
                return jsonify(user_data)
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/profile_picture', methods=['GET', 'POST'])
def profile_picture():
    user_id = session.get('user_id')
    if request.method == 'GET':
        if user_id:
            user = db.session.get(User, user_id)
            if user.image:
                return send_file(BytesIO(user.image), mimetype='image/jpeg')
            else:
                return send_file('static/style/icon-placeholder.png', mimetype='image/png')
        return jsonify({'error': 'User not found'}), 404
    elif request.method == 'POST':
        if user_id:
            file = request.files.get('profile_picture')
            if file:
                img = Image.open(file.stream)
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                user = db.session.get(User, user_id)
                user.image = img_byte_arr
                db.session.commit()
                return jsonify({'success': True, 'message': 'Profile picture updated'}), 200
            return jsonify({'error': 'No file uploaded'}), 400
        return jsonify({'error': 'User not found'}), 404

@app.route('/api/add_news', methods=['POST'])
def add_news_route():
    title = request.form['title']
    content = request.form['content']
    image = request.files['image']

    if image:
        img = Image.open(image.stream)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
    else:
        img_byte_arr = None

    # Удаление старой новости, если их больше 4
    news_count = db.session.query(News).count()
    if news_count >= 4:
        oldest_news = db.session.query(News).order_by(News.timestamp.asc()).first()
        db.session.delete(oldest_news)

    new_news = News(title=title, content=content, image=img_byte_arr)
    db.session.add(new_news)
    db.session.commit()

    return jsonify({"success": True, "message": "News added successfully"}), 200


@app.route('/api/get_news_image/<int:news_id>', methods=['GET'])
def get_news_image(news_id):
    news = db.session.get(News, news_id)
    if news and news.image:
        return send_file(BytesIO(news.image), mimetype='image/jpeg')
    return jsonify({"error": "Image not found"}), 404

@app.route('/api/add_physorg', methods=['POST'])
def add_physorg():
    surname = request.form['surname']
    name = request.form['name']
    patronymic = request.form['patronymic']
    gender = request.form['gender']
    group = request.form['group']
    login = request.form['login']
    password = request.form['password']

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    gender_id = db.session.query(Gender).filter_by(name=gender).first().id
    group_id = db.session.query(Group).filter_by(name=group).first().id

    new_user = User(
        roleID=2,
        surname=surname,
        name=name,
        patronymic=patronymic,
        login=login,
        password=hashed_password,
        genderID=gender_id,
        groupID=group_id
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"success": True, "message": "Physorg added successfully"}), 200

@app.route('/api/delete_profile_picture', methods=['POST'])
def delete_profile_picture():
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        user.image = None
        db.session.commit()
        return jsonify({"success": True, "message": "Profile picture deleted successfully"}), 200
    return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') != 'testing':
        print(f"FLASK_ENV is set to: {os.getenv('FLASK_ENV')}")  # Логирование значения переменной окружения
        with app.app_context():
            update_user_password('admin', 'admin')
        app.run(debug=True)
