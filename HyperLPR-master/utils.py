import pymysql
import cv2
import HyperLPRLite as pr

model = pr.LPR("model/cascade.xml", "model/model12.h5", "model/ocr_plate_all_gru.h5")

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='3218560376jJ',
        database='2',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def create_users_table_if_not_exists():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    conn.commit()
    conn.close()

def recognize_from_photo(file_path):
    image = cv2.imread(file_path)
    results = model.SimpleRecognizePlateByE2E(image)
    return results

def get_plate_type(plate, color):
    if "红" in color or plate.startswith("WJ"):
        return "武警车牌"
    elif "绿" in color:
        return "新能源车牌"
    else:
        return "普通车牌"

def get_province_info(plate):
    province_map = {
        "京": "北京市", "津": "天津市", "沪": "上海市", "渝": "重庆市", "冀": "河北省",
        "豫": "河南省", "云": "云南省", "辽": "辽宁省", "黑": "黑龙江省", "湘": "湖南省",
        "皖": "安徽省", "鲁": "山东省", "新": "新疆维吾尔自治区", "苏": "江苏省", "浙": "浙江省",
        "赣": "江西省", "鄂": "湖北省", "桂": "广西壮族自治区", "甘": "甘肃省", "晋": "山西省",
        "蒙": "内蒙古自治区", "陕": "陕西省", "吉": "吉林省", "闽": "福建省", "贵": "贵州省",
        "粤": "广东省", "青": "青海省", "藏": "西藏自治区", "川": "四川省", "宁": "宁夏回族自治区",
        "琼": "海南省", "使": "使馆", "警": "警牌", "学": "学牌", "港": "香港特别行政区",
        "澳": "澳门特别行政区", "台": "台湾省"
    }
    return province_map.get(plate[0], "未知省份")

def get_color_in_chinese(color):
    color_map = {
        "blue": "蓝色", "yellow": "黄色", "green": "绿色",
        "white": "白色", "black": "黑色", "red": "红色"
    }
    return color_map.get(color, "未知颜色")
