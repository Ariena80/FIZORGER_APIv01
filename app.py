from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__, template_folder='C:/Users/arien/OneDrive/Рабочий стол/Курсач удач/FIZORGER_HTML-main/templates', static_folder='C:/Users/arien/OneDrive/Рабочий стол/Курсач удач/FIZORGER_HTML-main/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://arien:12345678@fizorger'
app.config['SECRET_KEY'] = 'dde8a6ba4fdf7dbecb55874b5c03d02fd575d5ad4623e70c'

db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/media')
def media():
    return render_template('media.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/measure_upcoming')
def measure_upcoming():
    return render_template('measure_upcoming.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            return redirect(url_for('user_panel'))
        else:
            flash('Неверный логин или пароль')
    return render_template('login.html')

@app.route('/user_panel')
def user_panel():
    user_id = 1  # Пример ID пользователя
    user = User.query.get(user_id)

    if user:
        print(f"User found: {user.login}")
    else:
        print("User not found")
    return render_template('user_panel.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)

