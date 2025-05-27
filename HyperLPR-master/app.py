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

    # 绑定到 0.0.0.0，并使用环境变量 PORT（Render 默认 PORT=10000）
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 10000)),  # 本地开发默认用 5000
        debug=False  # 生产环境务必关闭 debug 模式！
    )
