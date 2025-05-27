import os
import uuid
import datetime
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from functools import wraps

from utils import (
    get_db_connection,
    recognize_from_photo,
    get_color_in_chinese,
    get_plate_type,
    get_province_info
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app, bcrypt):

    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/index', methods=['GET', 'POST'])
    @login_required
    def index():
        results_list = []
        image_path = ""
        if request.method == 'POST':
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                unique_name = str(uuid.uuid4()) + "_" + filename
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)

                results = recognize_from_photo(save_path)

                for result in results:
                    plate, confidence, rect, color = result
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    color_chinese = get_color_in_chinese(color)
                    plate_type = get_plate_type(plate, color_chinese)
                    province_info = get_province_info(plate)

                    results_list.append({
                        'plate': plate,
                        'confidence': confidence,
                        'color': color_chinese,
                        'current_time': current_time,
                        'province_info': province_info,
                        'plate_type': plate_type
                    })

                image_path = url_for('static', filename='uploads/' + unique_name)

        return render_template('index.html', results=results_list, image_path=image_path)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']

            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE username=%s OR email=%s"
                cursor.execute(sql, (username, email))
                user = cursor.fetchone()

                if user:
                    flash('用户名或邮箱已存在', 'danger')
                    conn.close()
                    return redirect(url_for('register'))

                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                sql_insert = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql_insert, (username, email, hashed_password))
                conn.commit()
            conn.close()

            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('index'))

        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = get_db_connection()
            with conn.cursor() as cursor:
                sql = "SELECT * FROM users WHERE email=%s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
            conn.close()

            if user and bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                flash('登录成功', 'success')
                return redirect(url_for('index'))
            else:
                flash('登录失败，请检查邮箱和密码', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('您已登出', 'success')
        return redirect(url_for('login'))
