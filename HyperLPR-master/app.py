from flask import Flask
from flask_bcrypt import Bcrypt
from routes import init_routes
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.secret_key = 'your-secret-key'

bcrypt = Bcrypt(app)

# 初始化数据库表
from utils import create_users_table_if_not_exists
create_users_table_if_not_exists()

# 注册路由
init_routes(app, bcrypt)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
