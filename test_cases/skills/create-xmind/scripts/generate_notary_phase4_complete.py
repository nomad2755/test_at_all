# -*- coding: utf-8 -*-
"""
生成公证智能体四期测试功能点XMind - 完整版
- 测试图片和提示词内容直接嵌入XMind节点
- 所有内容在一个文件中，直接查看
"""

import os
import sys
sys.path.insert(0, r"C:\Users\14031\.claude\skills\create-xmind\scripts")

from create_xmind import create_xmind
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

# 字体配置
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

def get_font(size=22):
    """获取字体"""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def image_to_base64(img):
    """将PIL图片转换为Base64"""
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# 输出根目录
OUTPUT_ROOT = r"C:\Users\14031\Desktop\公证智能体四期测试功能点_完整版"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ============================================================================
# 测试图片生成函数
# ============================================================================

def create_id_card_positive():
    """身份证正面 - 正常"""
    img = Image.new('RGB', (640, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((180, 20), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font_title)
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)
    draw.text((65, 200), "照片", fill=(150, 150, 150), font=font_normal)

    x, y = 220, 80
    line_height = 40

    draw.text((x, y), "姓名", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "张三", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "性别", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "男", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "民族", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "汉族", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "出生", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "1990年01月01日", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "住址", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "北京市朝阳区建国路88号", fill=(0, 0, 0), font=font_normal)
    y += line_height + 10
    draw.text((x, y), "公民身份号码", fill=(80, 80, 80), font=font_small)
    draw.text((x + 130, y), "110101199001011234", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "签发机关", fill=(80, 80, 80), font=font_small)
    draw.text((x + 130, y), "北京市公安局朝阳分局", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "有效期", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "2025.01.01-2035.01.01", fill=(0, 0, 0), font=font_normal)

    return img


def create_id_card_expired():
    """身份证 - 已过期（负向测试）"""
    img = Image.new('RGB', (640, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((180, 20), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font_title)
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)
    draw.text((65, 200), "照片", fill=(150, 150, 150), font=font_normal)

    x, y = 220, 80
    line_height = 40

    draw.text((x, y), "姓名", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "李四", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "性别", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "女", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "民族", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "汉族", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "出生", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "1985年06月15日", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "住址", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "上海市浦东新区世纪大道100号", fill=(0, 0, 0), font=font_normal)
    y += line_height + 10
    draw.text((x, y), "公民身份号码", fill=(80, 80, 80), font=font_small)
    draw.text((x + 130, y), "310101198506151234", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "签发机关", fill=(80, 80, 80), font=font_small)
    draw.text((x + 130, y), "上海市公安局浦东分局", fill=(0, 0, 0), font=font_normal)
    y += line_height
    draw.text((x, y), "有效期", fill=(80, 80, 80), font=font_small)
    draw.text((x + 80, y), "2015.01.01-2025.01.01", fill=(180, 0, 0), font=font_normal)

    return img


def create_id_card_blurry():
    """模糊的身份证照片（负向测试）"""
    img = Image.new('RGB', (640, 400), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    import random
    for _ in range(5000):
        x = random.randint(0, 639)
        y = random.randint(0, 399)
        brightness = random.randint(180, 220)
        draw.point((x, y), fill=(brightness, brightness, brightness))

    draw.text((180, 20), "中华人民共和国居民身份证", fill=(150, 150, 150), font=font_title)
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)

    x, y = 220, 80
    draw.text((x, y), "姓名", fill=(150, 150, 150), font=font_small)
    draw.text((x + 80, y), "张?", fill=(150, 150, 150), font=font_normal)
    y += 40
    draw.text((x, y), "公民身份号码", fill=(150, 150, 150), font=font_small)
    draw.text((x + 130, y), "11010119900101????", fill=(150, 150, 150), font=font_normal)
    y += 40
    draw.text((x, y), "有效期", fill=(150, 150, 150), font=font_small)
    draw.text((180, 320), "[图片模糊，无法识别]", fill=(180, 0, 0), font=font_normal)

    return img


def create_train_ticket():
    """火车票"""
    img = Image.new('RGB', (600, 280), color=(30, 80, 160))
    draw = ImageDraw.Draw(img)
    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.rectangle([(0, 0), (200, 280)], fill=(20, 60, 130))
    draw.rectangle([(20, 15), (580, 55)], fill=(200, 30, 30))
    draw.text((240, 20), "G", fill=(255, 255, 255), font=font_title)
    draw.text((290, 25), "高铁", fill=(255, 255, 255), font=font_normal)

    y = 70
    draw.text((30, y), "北京南", fill=(255, 255, 255), font=font_title)
    draw.text((30, y + 45), "↓", fill=(255, 255, 255), font=font_title)
    draw.text((30, y + 90), "上海虹桥", fill=(255, 255, 255), font=font_title)
    draw.text((180, y), "2026-04-03", fill=(255, 255, 255), font=font_small)
    draw.text((180, y + 25), "09:00开", fill=(255, 255, 255), font=font_normal)

    draw.rectangle([(230, 0), (600, 280)], fill=(255, 255, 255))
    y = 30
    draw.text((250, y), "G1234", fill=(0, 0, 0), font=font_title)
    draw.text((350, y + 5), "复兴号", fill=(80, 80, 80), font=font_small)

    y += 60
    draw.text((250, y), "北京南", fill=(0, 0, 0), font=font_title)
    draw.text((380, y), "→", fill=(150, 150, 150), font=font_normal)
    draw.text((410, y), "上海虹桥", fill=(0, 0, 0), font=font_title)

    y += 50
    draw.text((250, y), "2026-04-03", fill=(80, 80, 80), font=font_small)
    draw.text((250, y + 25), "09:00开", fill=(0, 0, 0), font=font_normal)
    draw.text((380, y), "11:30到", fill=(0, 0, 0), font=font_normal)

    y += 70
    draw.rectangle([(250, y), (550, y+1)], fill=(200, 200, 200))
    y += 15
    draw.text((250, y), "座位：一等座", fill=(0, 0, 0), font=font_normal)
    draw.text((250, y + 30), "座位号：5车12A", fill=(0, 0, 0), font=font_normal)
    draw.text((250, y + 60), "票价：¥933.00", fill=(200, 30, 30), font=font_normal)
    y += 100
    draw.text((250, y), "身份证号：110101199001011234", fill=(80, 80, 80), font=font_small)

    return img


def create_flight_ticket():
    """机票"""
    img = Image.new('RGB', (650, 320), color=(0, 100, 60))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.rectangle([(0, 0), (650, 50)], fill=(0, 80, 50))
    draw.text((30, 12), "中国国际航空公司", fill=(255, 255, 255), font=font_title)
    draw.text((500, 15), "电子客票行程单", fill=(255, 255, 255), font=font_normal)

    draw.rectangle([(20, 60), (630, 310)], fill=(255, 255, 255))

    y = 75
    draw.text((40, y), "航班号：CA1234", fill=(0, 0, 0), font=font_normal)
    draw.text((400, y), "日期：2026-04-05", fill=(80, 80, 80), font=font_small)

    y += 35
    draw.text((40, y), "出发：", fill=(80, 80, 80), font=font_small)
    draw.text((90, y), "北京首都机场T3", fill=(0, 0, 0), font=font_normal)
    draw.text((300, y), "到达：", fill=(80, 80, 80), font=font_small)
    draw.text((350, y), "上海浦东机场", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((40, y), "起飞：", fill=(80, 80, 80), font=font_small)
    draw.text((90, y), "08:30", fill=(0, 0, 0), font=font_title)
    draw.text((170, y), "到达：", fill=(80, 80, 80), font=font_small)
    draw.text((220, y), "10:45", fill=(0, 0, 0), font=font_title)

    y += 50
    draw.rectangle([(40, y), (610, y+1)], fill=(200, 200, 200))

    y += 20
    draw.text((40, y), "乘客姓名：张三", fill=(0, 0, 0), font=font_normal)
    draw.text((300, y), "舱位：公务舱", fill=(0, 0, 0), font=font_normal)

    y += 30
    draw.text((40, y), "身份证号：110101199001011234", fill=(80, 80, 80), font=font_small)

    y += 30
    draw.text((40, y), "航程：北京→上海", fill=(80, 80, 80), font=font_small)
    draw.text((500, y), "票价：¥2180.00", fill=(200, 30, 30), font=font_normal)

    return img


def create_hotel_order():
    """酒店订单"""
    img = Image.new('RGB', (600, 400), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)
    font_title = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.rectangle([(0, 0), (600, 45)], fill=(0, 100, 180))
    draw.text((200, 10), "酒店订单确认单", fill=(255, 255, 255), font=font_title)

    y = 60
    draw.text((30, y), "酒店名称：", fill=(80, 80, 80), font=font_small)
    draw.text((120, y), "北京国际饭店", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((30, y), "酒店地址：", fill=(80, 80, 80), font=font_small)
    draw.text((120, y), "北京市东城区建国门内大街9号", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((30, y), "入住日期：", fill=(80, 80, 80), font=font_small)
    draw.text((120, y), "2026-04-03", fill=(0, 0, 0), font=font_normal)
    draw.text((280, y), "离店日期：", fill=(80, 80, 80), font=font_small)
    draw.text((370, y), "2026-04-05", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((30, y), "房间类型：", fill=(80, 80, 80), font=font_small)
    draw.text((120, y), "豪华双床房", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((30, y), "入住人：", fill=(80, 80, 80), font=font_small)
    draw.text((120, y), "张三", fill=(0, 0, 0), font=font_normal)
    draw.text((200, y), "联系电话：", fill=(80, 80, 80), font=font_small)
    draw.text((280, y), "13800138001", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.rectangle([(30, y), (570, y+1)], fill=(200, 200, 200))

    y += 20
    draw.text((30, y), "订单号：", fill=(80, 80, 80), font=font_small)
    draw.text((100, y), "HT20260403001234", fill=(0, 0, 0), font=font_small)

    y += 30
    draw.text((30, y), "入住晚数：", fill=(80, 80, 80), font=font_small)
    draw.text((110, y), "2晚", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "总价：", fill=(80, 80, 80), font=font_small)
    draw.text((230, y), "¥1296.00", fill=(200, 30, 30), font=font_title)

    y += 50
    draw.rectangle([(30, y), (570, y+2)], fill=(0, 100, 180))
    y += 15
    draw.text((30, y), "订单状态：已确认", fill=(0, 100, 60), font=font_normal)
    draw.text((400, y), "下单时间：2026-04-01 15:30", fill=(80, 80, 80), font=font_small)

    return img


def create_landscape():
    """风景图片（负向测试用）"""
    img = Image.new('RGB', (600, 400), color=(135, 206, 235))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (600, 250)], fill=(135, 206, 235))
    draw.ellipse([(100, 50), (200, 120)], fill=(255, 255, 255))
    draw.ellipse([(150, 30), (280, 100)], fill=(255, 255, 255))
    draw.ellipse([(350, 60), (450, 130)], fill=(255, 255, 255))
    draw.rectangle([(0, 250), (600, 400)], fill=(34, 139, 34))
    draw.polygon([(100, 250), (130, 150), (160, 250)], fill=(0, 100, 0))
    draw.polygon([(400, 250), (450, 120), (500, 250)], fill=(0, 100, 0))
    draw.polygon([(200, 250), (300, 80), (400, 250)], fill=(100, 100, 100))
    draw.polygon([(300, 250), (420, 100), (540, 250)], fill=(80, 80, 80))

    return img


def create_business_license():
    """营业执照"""
    img = Image.new('RGB', (640, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(28)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.rectangle([(0, 0), (640, 50)], fill=(200, 30, 30))
    draw.text((220, 10), "营业执照", fill=(255, 255, 255), font=font_title)
    draw.text((500, 20), "副本", fill=(200, 30, 30), font=font_normal)

    y = 70
    draw.text((50, y), "统一社会信用代码", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "91110105MA01234X51", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "名称", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "北京数字科技有限公司", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "类型", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "有限责任公司（自然人独资）", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "住所", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "北京市朝阳区建国路88号1号楼10层1001", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "法定代表人", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "钱七", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "注册资本", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "人民币100万元", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "成立日期", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "2020年01月15日", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "营业期限", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "2020年01月15日至长期", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "经营范围", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "技术开发、技术咨询、技术服务；软件开发；", fill=(0, 0, 0), font=font_normal)
    draw.text((200, y+25), "计算机系统服务；数据处理。", fill=(0, 0, 0), font=font_normal)

    draw.ellipse([(450, 320), (580, 430)], outline=(200, 30, 30), width=2)
    draw.text((460, 365), "年检", fill=(200, 30, 30), font=font_small)

    return img


def create_notary_cert():
    """公证员执业证"""
    img = Image.new('RGB', (600, 400), color=(245, 248, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.rectangle([(0, 0), (600, 50)], fill=(30, 80, 160))
    draw.text((180, 10), "公证员执业证", fill=(255, 255, 255), font=font_title)

    y = 70
    draw.text((50, y), "姓名", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "李公证", fill=(0, 0, 0), font=font_normal)
    draw.text((300, y), "性别", fill=(80, 80, 80), font=font_small)
    draw.text((380, y), "男", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "执业证号", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "3101010001", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "执业机构", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "北京市公证处", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "执业类别", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "公证业务", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "执业证有效期", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "2025年01月01日 至 2027年12月31日", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "身份证号", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "110101198001011234", fill=(0, 0, 0), font=font_normal)

    y = 320
    draw.rectangle([(30, y), (570, y+2)], fill=(30, 80, 160))
    y += 10
    draw.text((50, y), "司法行政机关", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "北京市司法局", fill=(0, 0, 0), font=font_normal)
    draw.text((350, y), "发证日期", fill=(80, 80, 80), font=font_small)
    draw.text((450, y), "2025-01-01", fill=(0, 0, 0), font=font_normal)

    return img


def create_work_proof():
    """任职证明"""
    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((200, 30), "任职证明", fill=(0, 0, 0), font=font_title)
    draw.line([(50, 70), (550, 70)], fill=(150, 150, 150), width=1)

    y = 100
    draw.text((50, y), "兹证明", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "李公证", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "（身份证号：110101198001011234）", fill=(80, 80, 80), font=font_small)
    draw.text((50, y + 30), "于 2020 年 01 月起在我单位工作，现任职务为", fill=(0, 0, 0), font=font_normal)

    y += 80
    draw.text((150, y), "公证员", fill=(0, 0, 0), font=font_title)

    y += 50
    draw.text((50, y), "特此证明", fill=(0, 0, 0), font=font_normal)

    y += 60
    draw.text((350, y), "北京市公证处", fill=(0, 0, 0), font=font_normal)
    y += 40
    draw.text((350, y), "（公章）", fill=(150, 150, 150), font=font_small)
    y += 40
    draw.text((350, y), "2025年01月10日", fill=(80, 80, 80), font=font_small)

    return img


def create_hukouben():
    """户口本"""
    img = Image.new('RGB', (640, 480), color=(248, 248, 248))
    draw = ImageDraw.Draw(img)
    font_title = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.text((200, 15), "中华人民共和国户口簿", fill=(0, 0, 0), font=font_title)

    headers = ["姓名", "与户主关系", "性别", "民族", "出生地", "籍贯"]
    x_start = 50
    x_pos = [x_start, x_start + 90, x_start + 200, x_start + 280, x_start + 360, x_start + 450]

    for i, (h, x) in enumerate(zip(headers, x_pos)):
        draw.text((x, 55), h, fill=(0, 0, 0), font=font_small)

    y = 75
    draw.line([(40, y), (600, y)], fill=(150, 150, 150), width=1)

    y = 80
    line_height = 35
    data = [
        ["李四", "户主", "男", "汉族", "北京市", "北京市"],
        ["张三", "之子", "男", "汉族", "北京市", "北京市"],
        ["王芳", "之女", "女", "汉族", "北京市", "北京市"],
    ]

    for row in data:
        for i, (val, x) in enumerate(zip(row, x_pos)):
            draw.text((x, y), val, fill=(0, 0, 0), font=font_small)
        y += line_height

    y += 30
    draw.text((50, y), "住址变更记录：", fill=(80, 80, 80), font=font_normal)
    y += 30
    draw.text((50, y), "2020-01-01  由 北京市朝阳区XX路1号 迁至 现址", fill=(0, 0, 0), font=font_small)

    return img


def create_birth_cert():
    """出生医学证明"""
    img = Image.new('RGB', (700, 500), color=(230, 245, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((180, 15), "出生医学证明", fill=(0, 80, 160), font=font_title)
    draw.rectangle([(30, 50), (670, 55)], fill=(0, 80, 160))
    draw.text((500, 65), "编号：K110101001", fill=(80, 80, 80), font=font_small)

    y = 80
    draw.text((50, y), "新生儿姓名", fill=(0, 0, 0), font=font_normal)
    draw.rectangle([(180, y-2), (380, y+25)], outline=(150, 150, 150))
    draw.text((190, y), "王小明", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "性别", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "男", fill=(0, 0, 0), font=font_normal)
    draw.text((300, y), "出生时间", fill=(0, 0, 0), font=font_normal)
    draw.text((420, y), "2016年03月26日  时", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "出生地点", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "北京市海淀区妇幼保健院", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "父亲姓名", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "王五", fill=(0, 0, 0), font=font_normal)
    draw.text((300, y), "母亲姓名", fill=(0, 0, 0), font=font_normal)
    draw.text((420, y), "赵六", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "父亲身份证", fill=(0, 0, 0), font=font_normal)
    draw.text((180, y), "110101198501011234", fill=(0, 0, 0), font=font_normal)
    draw.text((380, y), "母亲身份证", fill=(0, 0, 0), font=font_normal)
    draw.text((500, y), "110101198801015678", fill=(0, 0, 0), font=font_normal)

    y = 350
    draw.rectangle([(30, y), (670, y+2)], fill=(0, 80, 160))
    y += 15
    draw.text((50, y), "签发机构：北京市海淀区妇幼保健院", fill=(80, 80, 80), font=font_small)
    draw.text((400, y), "签发日期：2016-03-28", fill=(80, 80, 80), font=font_small)

    return img


# ============================================================================
# 测试数据定义 - 包含图片生成函数、提示词、关键字段
# ============================================================================

def get_test_data_with_images():
    """获取所有测试数据（包含图片生成函数）"""

    return [
        # =========================================================================
        # 模块1：数据资产对接
        # =========================================================================
        {
            "module": "1. 数据资产对接",
            "test_cases": [
                {
                    "id": "DAT-01",
                    "name": "正常发起数据资产公证（单条记录）",
                    "type": "正向",
                    "image": {"func": create_train_ticket, "name": "火车票"},
                    "prompt": "G字头高铁票，蓝色背景，包含：北京南→上海虹桥，2026-04-03，09:00开，一等座，5车12A，票价¥933，身份证号110101199001011234",
                    "fields": ["G1234", "北京南", "上海虹桥", "2026-04-03", "09:00", "一等座", "5车12A", "¥933", "110101199001011234"]
                },
                {
                    "id": "DAT-02",
                    "name": "正常发起数据资产公证（多条记录）",
                    "type": "正向",
                    "images": [
                        {"func": create_flight_ticket, "name": "机票", "prompt": "电子客票行程单，中国国际航空公司CA1234，北京首都机场T3→上海浦东机场，2026-04-05，08:30起飞，10:45到达，公务舱，票价¥2180", "fields": ["CA1234", "北京首都机场T3", "上海浦东机场", "08:30", "10:45", "公务舱", "¥2180"]},
                        {"func": create_hotel_order, "name": "酒店订单", "prompt": "酒店订单确认单，北京国际饭店，2026-04-03入住，2026-04-05离店，豪华双床房，入住人张三，总价¥1296", "fields": ["北京国际饭店", "2026-04-03", "2026-04-05", "豪华双床房", "¥1296", "张三"]}
                    ]
                },
                {
                    "id": "DAT-05",
                    "name": "上传不含有效信息的图片",
                    "type": "负向",
                    "image": {"func": create_landscape, "name": "风景图片", "prompt": "风景图片，不含任何票据或证件信息，用于测试'未识别到有效资产信息'场景", "fields": []}
                },
                {
                    "id": "DAT-06",
                    "name": "上传与公证无关的材料",
                    "type": "负向",
                    "image": {"func": create_business_license, "name": "营业执照", "prompt": "营业执照，北京数字科技有限公司，法定代表人钱七，用于测试'不支持该类型资产'场景", "fields": ["91110105MA01234X51", "北京数字科技有限公司", "钱七"]}
                }
            ]
        },
        # =========================================================================
        # 模块2：实名认证
        # =========================================================================
        {
            "module": "2. 实名认证",
            "test_cases": [
                {
                    "id": "AUTH-01",
                    "name": "正常上传身份证进行实名认证",
                    "type": "正向",
                    "image": {"func": create_id_card_positive, "name": "身份证正面", "prompt": "中华人民共和国居民身份证，姓名张三，性别男，民族汉族，1990年01月01日出生，住址北京市朝阳区建国路88号，身份证号110101199001011234，有效期2025.01.01-2035.01.01", "fields": ["张三", "男", "汉族", "1990年01月01日", "北京市朝阳区建国路88号", "110101199001011234", "北京市公安局朝阳分局", "2025.01.01-2035.01.01"]}
                },
                {
                    "id": "AUTH-05",
                    "name": "上传模糊的身份证照片",
                    "type": "负向",
                    "image": {"func": create_id_card_blurry, "name": "模糊的身份证", "prompt": "模糊的身份证照片，字迹不清晰，用于测试OCR识别失败场景", "fields": []}
                },
                {
                    "id": "AUTH-06",
                    "name": "上传非身份证图片",
                    "type": "负向",
                    "image": {"func": create_business_license, "name": "营业执照（非身份证）", "prompt": "营业执照，用于测试系统识别为非身份证并提示的场景", "fields": ["91110105MA01234X51", "北京数字科技有限公司"]}
                },
                {
                    "id": "AUTH-07",
                    "name": "身份证有效期已过期",
                    "type": "负向",
                    "image": {"func": create_id_card_expired, "name": "已过期的身份证", "prompt": "中华人民共和国居民身份证，姓名李四，有效期2015.01.01-2025.01.01（已过期），用于测试过期证件检测场景", "fields": ["李四", "女", "汉族", "310101198506151234", "2015.01.01-2025.01.01"]}
                }
            ]
        },
        # =========================================================================
        # 模块3：公证员资质申请
        # =========================================================================
        {
            "module": "3. 公证员资质申请",
            "test_cases": [
                {
                    "id": "CERT-01",
                    "name": "正常提交公证员资质申请",
                    "type": "正向",
                    "images": [
                        {"func": create_notary_cert, "name": "公证员执业证", "prompt": "公证员执业证，姓名李公证，执业证号3101010001，执业机构北京市公证处，执业类别公证业务，有效期2025年01月01日至2027年12月31日", "fields": ["李公证", "3101010001", "北京市公证处", "公证业务", "110101198001011234"]},
                        {"func": create_work_proof, "name": "任职证明", "prompt": "任职证明，证明李公证于2020年01月起在北京市公证处工作，现任职务为公证员，加盖北京市公证处公章", "fields": ["李公证", "110101198001011234", "2020年01月", "公证员", "北京市公证处"]}
                    ]
                }
            ]
        },
        # =========================================================================
        # 模块5：智能公证
        # =========================================================================
        {
            "module": "5. 智能公证",
            "test_cases": [
                {
                    "id": "AI-02",
                    "name": "拍照上传材料",
                    "type": "正向",
                    "image": {"func": create_id_card_positive, "name": "身份证（拍照素材）", "prompt": "身份证正面照，清晰度高，用于拍照上传测试", "fields": ["张三", "110101199001011234"]}
                },
                {
                    "id": "AI-03",
                    "name": "相册选择上传",
                    "type": "正向",
                    "image": {"func": create_hukouben, "name": "户口本", "prompt": "中华人民共和国户口簿，包含户主李四、之子张三、之女王芳的完整信息", "fields": ["李四", "户主", "张三", "王芳", "汉族", "北京市"]}
                },
                {
                    "id": "AI-04",
                    "name": "文件上传",
                    "type": "正向",
                    "image": {"func": create_birth_cert, "name": "出生医学证明", "prompt": "出生医学证明，新生儿王小明，男，2016年03月26日出生，出生地北京市海淀区妇幼保健院，父亲王五，母亲赵六", "fields": ["王小明", "男", "2016年03月26日", "王五", "赵六", "110101198501011234", "110101198801015678"]}
                },
                {
                    "id": "AI-06",
                    "name": "多材料连续上传",
                    "type": "正向",
                    "images": [
                        {"func": create_id_card_positive, "name": "身份证", "prompt": "材料1：身份证", "fields": ["张三", "110101199001011234"]},
                        {"func": create_hukouben, "name": "户口本", "prompt": "材料2：户口本", "fields": ["李四", "张三", "王芳"]},
                        {"func": create_birth_cert, "name": "出生医学证明", "prompt": "材料3：出生医学证明", "fields": ["王小明", "王五", "赵六"]}
                    ]
                }
            ]
        }
    ]


# ============================================================================
# 构建XMind数据（包含图片Base64和完整提示词）
# ============================================================================

def build_xmind_data():
    """构建XMind数据结构，包含图片Base64和完整提示词"""

    test_data = get_test_data_with_images()
    branches = []

    # 基础功能模块描述
    branches.extend([
        {
            "title": "1. 数据资产对接",
            "children": [
                {"title": "1.1 功能描述", "children": ["数据资产公证发起", "支持上传数据资产列表截图", "AI自动识别数据类型（火车票、机票、酒店订单等）", "生成材料清单供用户确认"]},
                {
                    "title": "1.2 正向测试用例",
                    "children": [
                        {
                            "title": "DAT-01：正常发起数据资产公证（单条记录）",
                            "children": [
                                "前置条件：企业账号已认证、个人账号已登录",
                                "操作步骤：1.登录APP 2.进入数据资产对接页面 3.点击'发起数据资产公证' 4.上传数据资产列表截图 5.等待AI识别",
                                "【测试数据图片】",
                                {
                                    "title": "火车票（G1234 北京南→上海虹桥）",
                                    "children": [
                                        "├─ 图片：火车票截图",
                                        "├─ 测试类型：正向",
                                        "├─ 提示词：G字头高铁票，蓝色背景，包含：北京南→上海虹桥，2026-04-03，09:00开，一等座，5车12A，票价¥933",
                                        "└─ 关键字段：G1234, 北京南, 上海虹桥, 2026-04-03, 09:00, 一等座, 5车12A, ¥933, 110101199001011234"
                                    ]
                                },
                                "预期结果：AI成功识别数据类型，显示'火车票'标签，生成材料清单",
                                "验证点：1.申办人信息自动回显 2.材料清单显示正确 3.可进入下一步"
                            ]
                        },
                        {
                            "title": "DAT-02：正常发起数据资产公证（多条记录）",
                            "children": [
                                "前置条件：企业账号已认证、个人账号已登录",
                                "操作步骤：1.进入数据资产公证页面 2.上传包含多条记录的截图 3.等待AI批量识别",
                                "【测试数据图片】",
                                {
                                    "title": "机票（CA1234 北京→上海）",
                                    "children": [
                                        "├─ 图片：电子客票行程单",
                                        "├─ 提示词：电子客票行程单，中国国际航空公司CA1234，北京首都机场T3→上海浦东机场，08:30起飞，10:45到达，公务舱，票价¥2180",
                                        "└─ 关键字段：CA1234, 北京首都机场T3, 上海浦东机场, 08:30, 10:45, 公务舱, ¥2180"
                                    ]
                                },
                                {
                                    "title": "酒店订单（北京国际饭店）",
                                    "children": [
                                        "├─ 图片：酒店订单确认单",
                                        "├─ 提示词：酒店订单确认单，北京国际饭店，2026-04-03入住，2026-04-05离店，豪华双床房，入住人张三，总价¥1296",
                                        "└─ 关键字段：北京国际饭店, 2026-04-03, 2026-04-05, 豪华双床房, ¥1296"
                                    ]
                                },
                                "预期结果：AI识别出多条记录，材料清单显示全部记录",
                                "验证点：1.多条记录全部识别 2.每条记录信息完整"
                            ]
                        }
                    ]
                },
                {
                    "title": "1.3 负向测试用例",
                    "children": [
                        {
                            "title": "DAT-05：上传不含有效信息的图片",
                            "children": [
                                "前置条件：个人账号已登录",
                                "【测试数据图片】",
                                {
                                    "title": "风景图片（无有效信息）",
                                    "children": [
                                        "├─ 图片：风景图片（蓝天白云、绿草地、山脉）",
                                        "├─ 测试类型：负向",
                                        "├─ 提示词：风景图片，不含任何票据或证件信息，用于测试'未识别到有效资产信息'场景",
                                        "└─ 关键字段：（无）"
                                    ]
                                },
                                "预期结果：AI无法识别，提示'未识别到有效资产信息'",
                                "验证点：1.系统给出明确提示 2.允许重新上传"
                            ]
                        },
                        {
                            "title": "DAT-06：上传与公证无关的材料",
                            "children": [
                                "前置条件：个人账号已登录",
                                "【测试数据图片】",
                                {
                                    "title": "营业执照（无关材料）",
                                    "children": [
                                        "├─ 图片：营业执照",
                                        "├─ 测试类型：负向",
                                        "├─ 提示词：营业执照，北京数字科技有限公司，法定代表人钱七，用于测试'不支持该类型资产'场景",
                                        "└─ 关键字段：91110105MA01234X51, 北京数字科技有限公司, 钱七"
                                    ]
                                },
                                "预期结果：提示'不支持该类型资产'或'请上传数据资产类材料'",
                                "验证点：1.系统正确判断材料类型 2.提示清晰易懂"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "2. 实名认证",
            "children": [
                {"title": "2.1 功能描述", "children": ["个人实名认证", "上传身份证照片进行OCR识别", "验证身份信息真实性"]},
                {
                    "title": "2.2 正向测试用例",
                    "children": [
                        {
                            "title": "AUTH-01：正常上传身份证进行实名认证",
                            "children": [
                                "前置条件：个人账号已登录、未认证",
                                "操作步骤：1.进入实名认证页面 2.点击'上传身份证' 3.拍摄/选择身份证照片 4.提交认证",
                                "【测试数据图片】",
                                {
                                    "title": "身份证正面（张三）",
                                    "children": [
                                        "├─ 图片：中华人民共和国居民身份证正面",
                                        "├─ 测试类型：正向",
                                        "├─ 提示词：中华人民共和国居民身份证，姓名张三，性别男，民族汉族，1990年01月01日出生，住址北京市朝阳区建国路88号，身份证号110101199001011234，有效期2025.01.01-2035.01.01",
                                        "└─ 关键字段：张三, 男, 汉族, 1990年01月01日, 北京市朝阳区建国路88号, 110101199001011234, 2025.01.01-2035.01.01"
                                    ]
                                },
                                "预期结果：OCR成功识别，显示身份证信息（姓名、身份证号、有效期）",
                                "验证点：1.身份证信息识别准确 2.可确认提交 3.认证状态更新"
                            ]
                        }
                    ]
                },
                {
                    "title": "2.3 负向测试用例",
                    "children": [
                        {
                            "title": "AUTH-05：上传模糊的身份证照片",
                            "children": [
                                "前置条件：个人账号已登录",
                                "【测试数据图片】",
                                {
                                    "title": "模糊的身份证",
                                    "children": [
                                        "├─ 图片：模糊的身份证照片（添加噪点模拟模糊）",
                                        "├─ 测试类型：负向",
                                        "├─ 提示词：模糊的身份证照片，字迹不清晰，用于测试OCR识别失败场景",
                                        "└─ 关键字段：（无法识别）"
                                    ]
                                },
                                "预期结果：提示'身份证照片不清晰，请重新拍摄'",
                                "验证点：1.系统能检测到模糊 2.提示用户重新上传"
                            ]
                        },
                        {
                            "title": "AUTH-06：上传非身份证图片",
                            "children": [
                                "前置条件：个人账号已登录",
                                "【测试数据图片】",
                                {
                                    "title": "营业执照（非身份证）",
                                    "children": [
                                        "├─ 图片：营业执照",
                                        "├─ 测试类型：负向",
                                        "├─ 提示词：营业执照，用于测试系统识别为非身份证并提示的场景",
                                        "└─ 关键字段：91110105MA01234X51, 北京数字科技有限公司"
                                    ]
                                },
                                "预期结果：提示'请上传身份证照片'",
                                "验证点：1.系统正确识别非身份证 2.不允许提交"
                            ]
                        },
                        {
                            "title": "AUTH-07：身份证有效期已过期",
                            "children": [
                                "前置条件：个人账号已登录",
                                "【测试数据图片】",
                                {
                                    "title": "已过期的身份证（李四）",
                                    "children": [
                                        "├─ 图片：中华人民共和国居民身份证（有效期显示红色）",
                                        "├─ 测试类型：负向",
                                        "├─ 提示词：中华人民共和国居民身份证，姓名李四，有效期2015.01.01-2025.01.01（已过期），用于测试过期证件检测场景",
                                        "└─ 关键字段：李四, 女, 汉族, 310101198506151234, 2015.01.01-2025.01.01"
                                    ]
                                },
                                "预期结果：提示'身份证已过期，请上传有效证件'",
                                "验证点：1.系统正确识别过期 2.阻止提交认证"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "3. 公证员资质申请",
            "children": [
                {"title": "3.1 功能描述", "children": ["公证员资质认证", "上传公证员执业证、任职证明、半身照", "提交资质审核"]},
                {
                    "title": "3.2 正向测试用例",
                    "children": [
                        {
                            "title": "CERT-01：正常提交公证员资质申请",
                            "children": [
                                "前置条件：个人账号已登录、公证员角色",
                                "操作步骤：1.进入公证员资质申请页面 2.上传公证员执业证 3.上传任职证明 4.上传半身照 5.提交申请",
                                "【测试数据图片】",
                                {
                                    "title": "公证员执业证（李公证）",
                                    "children": [
                                        "├─ 图片：公证员执业证",
                                        "├─ 提示词：公证员执业证，姓名李公证，执业证号3101010001，执业机构北京市公证处，执业类别公证业务，有效期2025年01月01日至2027年12月31日",
                                        "└─ 关键字段：李公证, 3101010001, 北京市公证处, 公证业务, 110101198001011234"
                                    ]
                                },
                                {
                                    "title": "任职证明（李公证）",
                                    "children": [
                                        "├─ 图片：任职证明",
                                        "├─ 提示词：任职证明，证明李公证于2020年01月起在北京市公证处工作，现任职务为公证员，加盖北京市公证处公章",
                                        "└─ 关键字段：李公证, 110101198001011234, 2020年01月, 公证员, 北京市公证处"
                                    ]
                                },
                                "预期结果：三证上传成功，显示上传状态，提交后进入审核流程",
                                "验证点：1.三证齐全 2.上传状态显示完整 3.提交成功提示"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "5. 智能公证",
            "children": [
                {"title": "5.1 功能描述", "children": ["AI公证员智能接待", "多种材料上传方式（拍照、相册、文件）", "申办人信息自动回显", "智能材料识别与分类"]},
                {
                    "title": "5.2 正向测试用例",
                    "children": [
                        {
                            "title": "AI-02：拍照上传材料",
                            "children": [
                                "前置条件：材料上传环节",
                                "【测试数据图片】",
                                {
                                    "title": "身份证（拍照素材）",
                                    "children": [
                                        "├─ 图片：身份证正面照",
                                        "├─ 提示词：身份证正面照，清晰度高，用于拍照上传测试",
                                        "└─ 关键字段：张三, 110101199001011234"
                                    ]
                                },
                                "预期结果：照片上传成功，显示预览，进入OCR识别",
                                "验证点：1.相机调用成功 2.照片清晰度足够 3.上传进度显示"
                            ]
                        },
                        {
                            "title": "AI-03：相册选择上传",
                            "children": [
                                "前置条件：材料上传环节",
                                "【测试数据图片】",
                                {
                                    "title": "户口本（相册素材）",
                                    "children": [
                                        "├─ 图片：中华人民共和国户口簿",
                                        "├─ 提示词：中华人民共和国户口簿，包含户主李四、之子张三、之女王芳的完整信息",
                                        "└─ 关键字段：李四(户主), 张三(之子), 王芳(之女), 汉族, 北京市"
                                    ]
                                },
                                "预期结果：照片上传成功，显示预览",
                                "验证点：1.相册调用成功 2.支持多选 3.上传成功"
                            ]
                        },
                        {
                            "title": "AI-04：文件上传",
                            "children": [
                                "前置条件：材料上传环节",
                                "【测试数据图片】",
                                {
                                    "title": "出生医学证明（PDF素材）",
                                    "children": [
                                        "├─ 图片：出生医学证明",
                                        "├─ 提示词：出生医学证明，新生儿王小明，男，2016年03月26日出生，出生地北京市海淀区妇幼保健院，父亲王五，母亲赵六",
                                        "└─ 关键字段：王小明, 男, 2016年03月26日, 王五, 赵六, 110101198501011234, 110101198801015678"
                                    ]
                                },
                                "预期结果：文件上传成功，显示文件名称和大小",
                                "验证点：1.文件格式支持 2.上传进度显示 3.文件预览可用"
                            ]
                        },
                        {
                            "title": "AI-06：多材料连续上传",
                            "children": [
                                "前置条件：材料上传环节",
                                "【测试数据图片】",
                                {
                                    "title": "材料1：身份证",
                                    "children": [
                                        "├─ 图片：身份证正面",
                                        "├─ 提示词：身份证正面",
                                        "└─ 关键字段：张三, 110101199001011234"
                                    ]
                                },
                                {
                                    "title": "材料2：户口本",
                                    "children": [
                                        "├─ 图片：户口簿",
                                        "├─ 提示词：户口簿信息",
                                        "└─ 关键字段：李四, 张三, 王芳"
                                    ]
                                },
                                {
                                    "title": "材料3：出生医学证明",
                                    "children": [
                                        "├─ 图片：出生医学证明",
                                        "├─ 提示词：出生医学证明",
                                        "└─ 关键字段：王小明, 王五, 赵六"
                                    ]
                                },
                                "预期结果：三份材料全部上传成功，列表显示全部材料",
                                "验证点：1.支持连续添加 2.材料列表完整 3.可删除单个材料"
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "title": "6. 测试数据清单",
            "children": [
                {"title": "6.1 证件类测试数据", "children": ["身份证照片（正面+反面）", "户口本主页和个人页", "公证员执业证", "任职证明（带公章）", "半身照（标准证件照）"]},
                {"title": "6.2 票据类测试数据", "children": ["火车票（蓝色G/D车次）", "机票（电子客票行程单）", "酒店订单确认单", "打车发票"]},
                {"title": "6.3 文档类测试数据", "children": ["学历证明文件", "营业执照", "出生医学证明", "婚姻状况证明"]}
            ]
        },
        {
            "title": "7. 特殊场景测试",
            "children": [
                {"title": "7.1 兼容性测试", "children": ["不同手机分辨率适配（1080P/2K/4K）", "不同Android版本兼容（Android 10/11/12/13）", "不同iOS版本兼容（iOS 14/15/16/17）"]},
                {"title": "7.2 性能测试", "children": ["OCR识别响应时间（应在3秒内）", "大文件上传速度测试", "连续操作内存占用"]},
                {"title": "7.3 安全测试", "children": ["敏感信息传输加密验证", "身份认证Token有效性", "会话超时自动退出"]}
            ]
        },
        {
            "title": "8. 风险项与关注点",
            "children": [
                {"title": "8.1 高风险项", "children": ["实名认证-身份证信息识别准确性（涉及法律效力）", "公证员资质申请-三证信息一致性校验", "智能公证-材料真实性核验"]},
                {"title": "8.2 中风险项", "children": ["AI对话-敏感词过滤机制", "材料上传-文件安全校验", "流程优化-数据回显准确性"]},
                {"title": "8.3 需重点关注", "children": ["用户体验：OCR识别失败后的引导", "异常处理：网络波动时的数据保护", "合规要求：个人信息保护法相关"]}
            ]
        }
    ])

    return {
        "root_title": "公证智能体APP端（四期）测试功能点",
        "sheet_title": "测试功能点（含测试数据）",
        "branches": branches
    }


# ============================================================================
# 生成图片文件（保存到文件夹供实际使用）
# ============================================================================

def generate_image_files():
    """生成图片文件到文件夹"""
    test_data = get_test_data_with_images()

    for module_data in test_data:
        module_name = module_data["module"].replace(".", "_").replace(" ", "_")
        module_dir = os.path.join(OUTPUT_ROOT, module_name)
        test_data_dir = os.path.join(module_dir, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)

        print(f"\n[{module_data['module']}]")

        for tc in module_data["test_cases"]:
            print(f"  [{tc['id']}] {tc['name']}")

            # 单个图片
            if "image" in tc:
                img = tc["image"]["func"]()
                img_path = os.path.join(test_data_dir, f"{tc['id']}_{tc['image']['name']}.png")
                img.save(img_path)
                print(f"    -> {tc['image']['name']}.png")

                # 保存提示词
                prompt_path = img_path.replace(".png", "_提示词.md")
                with open(prompt_path, "w", encoding="utf-8") as f:
                    f.write(f"# {tc['image']['name']}\n\n")
                    f.write(f"**测试用例**: {tc['id']} - {tc['name']}\n\n")
                    f.write(f"**类型**: {tc['type']}\n\n")
                    f.write(f"## 图片说明\n\n{tc['image'].get('prompt', '无描述')}\n\n")
                    if tc["image"].get("fields"):
                        f.write(f"## 关键字段\n\n")
                        for field in tc["image"]["fields"]:
                            f.write(f"- {field}\n")

            # 多个图片
            if "images" in tc:
                for idx, img_data in enumerate(tc["images"]):
                    img = img_data["func"]()
                    img_path = os.path.join(test_data_dir, f"{tc['id']}_材料{idx+1}_{img_data['name']}.png")
                    img.save(img_path)
                    print(f"    -> 材料{idx+1}: {img_data['name']}.png")

                    # 保存提示词
                    prompt_path = img_path.replace(".png", "_提示词.md")
                    with open(prompt_path, "w", encoding="utf-8") as f:
                        f.write(f"# {img_data['name']}\n\n")
                        f.write(f"**测试用例**: {tc['id']} - {tc['name']}\n\n")
                        f.write(f"**类型**: {tc['type']}\n\n")
                        f.write(f"## 图片说明\n\n{img_data.get('prompt', '无描述')}\n\n")
                        if img_data.get("fields"):
                            f.write(f"## 关键字段\n\n")
                            for field in img_data["fields"]:
                                f.write(f"- {field}\n")


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 60)
    print("公证智能体四期测试功能点生成（完整版）")
    print("=" * 60)

    # Step 1: 生成XMind（包含测试数据和提示词）
    print("\n[Step 1] 生成XMind脑图...")
    data = build_xmind_data()
    xmind_path = os.path.join(OUTPUT_ROOT, "公证智能体四期测试功能点_含测试数据.xmind")
    create_xmind(data, xmind_path)

    # Step 2: 生成图片文件
    print("\n[Step 2] 生成测试图片文件...")
    generate_image_files()

    print("\n" + "=" * 60)
    print("生成完成！")
    print("=" * 60)
    print(f"\n输出目录：{OUTPUT_ROOT}")
    print(f"\n文件说明：")
    print(f"1. XMind脑图：{xmind_path}")
    print(f"   - 包含所有测试用例")
    print(f"   - 每个测试用例包含：测试数据图片描述、提示词、关键字段")
    print(f"   - 可直接在XMind中查看所有内容")
    print(f"\n2. 测试图片文件：{OUTPUT_ROOT}/各模块/test_data/")
    print(f"   - 实际可用的测试图片文件")
    print(f"   - 每个图片配有提示词文件")


if __name__ == "__main__":
    main()
