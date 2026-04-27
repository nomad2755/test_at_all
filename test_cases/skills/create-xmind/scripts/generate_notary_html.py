# -*- coding: utf-8 -*-
"""
生成公证智能体四期测试功能点 - HTML脑图版
- 支持直接在浏览器中查看嵌入的图片
- 包含完整的测试数据和提示词
"""

import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# 字体配置
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

def get_font(size=22):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

OUTPUT_ROOT = r"C:\Users\14031\Desktop\公证智能体四期测试功能点_HTML版"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ============================================================================
# 图片生成函数
# ============================================================================

def create_id_card_positive():
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

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# ============================================================================
# 测试数据定义
# ============================================================================

def get_test_data():
    return [
        {
            "module": "1. 数据资产对接",
            "test_cases": [
                {
                    "id": "DAT-01", "name": "正常发起数据资产公证（单条记录）", "type": "正向",
                    "prerequisite": "企业账号已认证、个人账号已登录",
                    "steps": "1.登录APP 2.进入数据资产对接页面 3.点击'发起数据资产公证' 4.上传数据资产列表截图 5.等待AI识别",
                    "images": [{"func": create_train_ticket, "name": "火车票", "prompt": "G字头高铁票，蓝色背景，包含：北京南→上海虹桥，2026-04-03，09:00开，一等座，5车12A，票价¥933", "fields": ["G1234", "北京南", "上海虹桥", "2026-04-03", "09:00", "一等座", "5车12A", "¥933", "110101199001011234"]}],
                    "expected": "AI成功识别数据类型，显示'火车票'标签，生成材料清单",
                    "verify": "1.申办人信息自动回显 2.材料清单显示正确 3.可进入下一步"
                },
                {
                    "id": "DAT-02", "name": "正常发起数据资产公证（多条记录）", "type": "正向",
                    "prerequisite": "企业账号已认证、个人账号已登录",
                    "steps": "1.进入数据资产公证页面 2.上传包含多条记录的截图 3.等待AI批量识别",
                    "images": [
                        {"func": create_flight_ticket, "name": "机票", "prompt": "电子客票行程单，中国国际航空公司CA1234，北京首都机场T3→上海浦东机场，08:30起飞，10:45到达，公务舱，票价¥2180", "fields": ["CA1234", "北京首都机场T3", "上海浦东机场", "08:30", "10:45", "公务舱", "¥2180"]},
                        {"func": create_hotel_order, "name": "酒店订单", "prompt": "酒店订单确认单，北京国际饭店，2026-04-03入住，2026-04-05离店，豪华双床房，入住人张三，总价¥1296", "fields": ["北京国际饭店", "2026-04-03", "2026-04-05", "豪华双床房", "¥1296"]}
                    ],
                    "expected": "AI识别出多条记录，材料清单显示全部记录",
                    "verify": "1.多条记录全部识别 2.每条记录信息完整"
                },
                {
                    "id": "DAT-05", "name": "上传不含有效信息的图片", "type": "负向",
                    "prerequisite": "个人账号已登录",
                    "images": [{"func": create_landscape, "name": "风景图片", "prompt": "风景图片，不含任何票据或证件信息，用于测试'未识别到有效资产信息'场景", "fields": []}],
                    "expected": "AI无法识别，提示'未识别到有效资产信息'",
                    "verify": "1.系统给出明确提示 2.允许重新上传"
                },
                {
                    "id": "DAT-06", "name": "上传与公证无关的材料", "type": "负向",
                    "prerequisite": "个人账号已登录",
                    "images": [{"func": create_business_license, "name": "营业执照", "prompt": "营业执照，北京数字科技有限公司，法定代表人钱七，用于测试'不支持该类型资产'场景", "fields": ["91110105MA01234X51", "北京数字科技有限公司", "钱七"]}],
                    "expected": "提示'不支持该类型资产'或'请上传数据资产类材料'",
                    "verify": "1.系统正确判断材料类型 2.提示清晰易懂"
                }
            ]
        },
        {
            "module": "2. 实名认证",
            "test_cases": [
                {
                    "id": "AUTH-01", "name": "正常上传身份证进行实名认证", "type": "正向",
                    "prerequisite": "个人账号已登录、未认证",
                    "steps": "1.进入实名认证页面 2.点击'上传身份证' 3.拍摄/选择身份证照片 4.提交认证",
                    "images": [{"func": create_id_card_positive, "name": "身份证正面", "prompt": "中华人民共和国居民身份证，姓名张三，性别男，民族汉族，1990年01月01日出生，住址北京市朝阳区建国路88号，身份证号110101199001011234，有效期2025.01.01-2035.01.01", "fields": ["张三", "男", "汉族", "1990年01月01日", "北京市朝阳区建国路88号", "110101199001011234", "2025.01.01-2035.01.01"]}],
                    "expected": "OCR成功识别，显示身份证信息（姓名、身份证号、有效期）",
                    "verify": "1.身份证信息识别准确 2.可确认提交 3.认证状态更新"
                },
                {
                    "id": "AUTH-05", "name": "上传模糊的身份证照片", "type": "负向",
                    "prerequisite": "个人账号已登录",
                    "images": [{"func": create_id_card_blurry, "name": "模糊的身份证", "prompt": "模糊的身份证照片，字迹不清晰，用于测试OCR识别失败场景", "fields": []}],
                    "expected": "提示'身份证照片不清晰，请重新拍摄'",
                    "verify": "1.系统能检测到模糊 2.提示用户重新上传"
                },
                {
                    "id": "AUTH-06", "name": "上传非身份证图片", "type": "负向",
                    "prerequisite": "个人账号已登录",
                    "images": [{"func": create_business_license, "name": "营业执照（非身份证）", "prompt": "营业执照，用于测试系统识别为非身份证并提示的场景", "fields": ["91110105MA01234X51", "北京数字科技有限公司"]}],
                    "expected": "提示'请上传身份证照片'",
                    "verify": "1.系统正确识别非身份证 2.不允许提交"
                },
                {
                    "id": "AUTH-07", "name": "身份证有效期已过期", "type": "负向",
                    "prerequisite": "个人账号已登录",
                    "images": [{"func": create_id_card_expired, "name": "已过期的身份证", "prompt": "中华人民共和国居民身份证，姓名李四，有效期2015.01.01-2025.01.01（已过期），用于测试过期证件检测场景", "fields": ["李四", "女", "汉族", "310101198506151234", "2015.01.01-2025.01.01"]}],
                    "expected": "提示'身份证已过期，请上传有效证件'",
                    "verify": "1.系统正确识别过期 2.阻止提交认证"
                }
            ]
        },
        {
            "module": "3. 公证员资质申请",
            "test_cases": [
                {
                    "id": "CERT-01", "name": "正常提交公证员资质申请", "type": "正向",
                    "prerequisite": "个人账号已登录、公证员角色",
                    "steps": "1.进入公证员资质申请页面 2.上传公证员执业证 3.上传任职证明 4.上传半身照 5.提交申请",
                    "images": [
                        {"func": create_notary_cert, "name": "公证员执业证", "prompt": "公证员执业证，姓名李公证，执业证号3101010001，执业机构北京市公证处，执业类别公证业务，有效期2025年01月01日至2027年12月31日", "fields": ["李公证", "3101010001", "北京市公证处", "公证业务", "110101198001011234"]},
                        {"func": create_work_proof, "name": "任职证明", "prompt": "任职证明，证明李公证于2020年01月起在北京市公证处工作，现任职务为公证员，加盖北京市公证处公章", "fields": ["李公证", "110101198001011234", "2020年01月", "公证员", "北京市公证处"]}
                    ],
                    "expected": "三证上传成功，显示上传状态，提交后进入审核流程",
                    "verify": "1.三证齐全 2.上传状态显示完整 3.提交成功提示"
                }
            ]
        },
        {
            "module": "5. 智能公证",
            "test_cases": [
                {
                    "id": "AI-02", "name": "拍照上传材料", "type": "正向",
                    "prerequisite": "材料上传环节",
                    "images": [{"func": create_id_card_positive, "name": "身份证（拍照素材）", "prompt": "身份证正面照，清晰度高，用于拍照上传测试", "fields": ["张三", "110101199001011234"]}],
                    "expected": "照片上传成功，显示预览，进入OCR识别",
                    "verify": "1.相机调用成功 2.照片清晰度足够 3.上传进度显示"
                },
                {
                    "id": "AI-03", "name": "相册选择上传", "type": "正向",
                    "prerequisite": "材料上传环节",
                    "images": [{"func": create_hukouben, "name": "户口本", "prompt": "中华人民共和国户口簿，包含户主李四、之子张三、之女王芳的完整信息", "fields": ["李四(户主)", "张三(之子)", "王芳(之女)", "汉族", "北京市"]}],
                    "expected": "照片上传成功，显示预览",
                    "verify": "1.相册调用成功 2.支持多选 3.上传成功"
                },
                {
                    "id": "AI-04", "name": "文件上传", "type": "正向",
                    "prerequisite": "材料上传环节",
                    "images": [{"func": create_birth_cert, "name": "出生医学证明", "prompt": "出生医学证明，新生儿王小明，男，2016年03月26日出生，出生地北京市海淀区妇幼保健院，父亲王五，母亲赵六", "fields": ["王小明", "男", "2016年03月26日", "王五", "赵六", "110101198501011234", "110101198801015678"]}],
                    "expected": "文件上传成功，显示文件名称和大小",
                    "verify": "1.文件格式支持 2.上传进度显示 3.文件预览可用"
                },
                {
                    "id": "AI-06", "name": "多材料连续上传", "type": "正向",
                    "prerequisite": "材料上传环节",
                    "images": [
                        {"func": create_id_card_positive, "name": "身份证", "prompt": "材料1：身份证正面", "fields": ["张三", "110101199001011234"]},
                        {"func": create_hukouben, "name": "户口本", "prompt": "材料2：户口簿信息", "fields": ["李四", "张三", "王芳"]},
                        {"func": create_birth_cert, "name": "出生医学证明", "prompt": "材料3：出生医学证明", "fields": ["王小明", "王五", "赵六"]}
                    ],
                    "expected": "三份材料全部上传成功，列表显示全部材料",
                    "verify": "1.支持连续添加 2.材料列表完整 3.可删除单个材料"
                }
            ]
        }
    ]

# ============================================================================
# 生成HTML脑图
# ============================================================================

def generate_html_mindmap():
    test_data = get_test_data()

    # 首先生成所有图片
    all_images = {}
    for module_data in test_data:
        for tc in module_data["test_cases"]:
            for img_info in tc.get("images", []):
                img = img_info["func"]()
                b64 = img_to_base64(img)
                img_id = f"{tc['id']}_{img_info['name']}"
                all_images[img_id] = {
                    "base64": b64,
                    "name": img_info["name"],
                    "prompt": img_info["prompt"],
                    "fields": img_info["fields"],
                    "tc_id": tc["id"],
                    "tc_name": tc["name"],
                    "tc_type": tc["type"]
                }

    # 生成HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公证智能体四期测试功能点 - 含测试数据图片</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", Arial, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }
.header h1 { font-size: 28px; margin-bottom: 10px; }
.header p { opacity: 0.9; font-size: 14px; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.module { background: #16213e; border-radius: 12px; margin-bottom: 30px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.module-header { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.module-header h2 { font-size: 20px; }
.module-header .toggle { font-size: 24px; transition: transform 0.3s; }
.module-header:hover { opacity: 0.95; }
.module-content { padding: 20px; display: none; }
.module-content.show { display: block; }
.test-case { background: #1f2937; border-radius: 10px; margin-bottom: 20px; overflow: hidden; border-left: 4px solid #667eea; }
.test-case.negative { border-left-color: #ef4444; }
.test-case-header { background: #374151; padding: 15px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.test-case-header:hover { background: #4b5563; }
.test-case-header h3 { font-size: 16px; color: #fff; }
.test-case-header .type-tag { padding: 4px 12px; border-radius: 20px; font-size: 12px; }
.type-tag.positive { background: #10b981; color: white; }
.type-tag.negative { background: #ef4444; color: white; }
.test-case-content { padding: 20px; display: none; }
.test-case-content.show { display: block; }
.info-row { display: flex; margin-bottom: 15px; padding: 10px; background: #374151; border-radius: 8px; }
.info-label { min-width: 100px; color: #9ca3af; font-size: 13px; }
.info-value { color: #fff; font-size: 14px; }
.image-section { margin-top: 20px; }
.image-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-top: 15px; }
.image-card { background: #374151; border-radius: 10px; overflow: hidden; }
.image-card img { width: 100%; height: auto; display: block; cursor: pointer; transition: transform 0.2s; }
.image-card img:hover { transform: scale(1.02); }
.image-info { padding: 15px; }
.image-info h4 { color: #667eea; margin-bottom: 10px; font-size: 14px; }
.image-info .prompt { color: #9ca3af; font-size: 13px; line-height: 1.6; margin-bottom: 10px; }
.image-info .fields { display: flex; flex-wrap: wrap; gap: 8px; }
.field-tag { background: #4b5563; padding: 4px 10px; border-radius: 15px; font-size: 12px; color: #d1d5db; }
/* Lightbox */
.lightbox { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: none; justify-content: center; align-items: center; z-index: 1000; cursor: zoom-out; }
.lightbox.show { display: flex; }
.lightbox img { max-width: 90%; max-height: 90%; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.lightbox-info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); padding: 15px 30px; border-radius: 30px; color: white; }
.summary { background: #16213e; border-radius: 12px; padding: 25px; margin-bottom: 30px; }
.summary h2 { color: #667eea; margin-bottom: 15px; }
.stats { display: flex; gap: 30px; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-number { font-size: 36px; font-weight: bold; color: #667eea; }
.stat-label { color: #9ca3af; font-size: 13px; }
.expand-btn { background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; margin-top: 10px; }
.expand-btn:hover { background: #5a67d8; }
</style>
</head>
<body>
<div class="header">
    <h1>公证智能体APP端（四期）测试功能点</h1>
    <p>包含测试数据图片 - 可直接在浏览器中查看 | 生成时间：2026-04-03</p>
</div>

<div class="container">
    <div class="summary">
        <h2>统计概览</h2>
        <div class="stats">
            <div class="stat"><div class="stat-number">''' + str(len(test_data)) + '''</div><div>模块数</div></div>
            <div class="stat"><div class="stat-number">''' + str(sum(len(tc["test_cases"]) for tc in test_data)) + '''</div><div>测试用例</div></div>
            <div class="stat"><div class="stat-number">''' + str(len(all_images)) + '''</div><div>测试图片</div></div>
            <div class="stat"><div class="stat-number">''' + str(sum(1 for tc_data in test_data for tc in tc_data["test_cases"] if tc["type"] == "正向")) + '''</div><div>正向用例</div></div>
            <div class="stat"><div class="stat-number">''' + str(sum(1 for tc_data in test_data for tc in tc_data["test_cases"] if tc["type"] == "负向")) + '''</div><div>负向用例</div></div>
        </div>
    </div>
'''

    # 生成模块和测试用例
    for module_data in test_data:
        html += f'''
    <div class="module">
        <div class="module-header" onclick="toggleModule(this)">
            <h2>{module_data["module"]}</h2>
            <span class="toggle">▼</span>
        </div>
        <div class="module-content">
'''
        for tc in module_data["test_cases"]:
            type_class = "negative" if tc["type"] == "负向" else "positive"
            html += f'''
            <div class="test-case {type_class}">
                <div class="test-case-header" onclick="toggleTestCase(this)">
                    <h3>{tc["id"]}：{tc["name"]}</h3>
                    <span class="type-tag {type_class}">{tc["type"]}</span>
                </div>
                <div class="test-case-content">
'''
            if tc.get("prerequisite"):
                html += f'''<div class="info-row"><span class="info-label">前置条件</span><span class="info-value">{tc["prerequisite"]}</span></div>'''
            if tc.get("steps"):
                html += f'''<div class="info-row"><span class="info-label">操作步骤</span><span class="info-value">{tc["steps"]}</span></div>'''
            if tc.get("images"):
                html += '''<div class="image-section"><h4>测试数据图片</h4><div class="image-grid">'''
                for img_info in tc["images"]:
                    img_id = f"{tc['id']}_{img_info['name']}"
                    img_data = all_images.get(img_id, {})
                    fields_html = "".join([f'<span class="field-tag">{f}</span>' for f in img_info["fields"]]) if img_info["fields"] else '<span class="field-tag" style="background:#ef4444">无关键字段（用于失败场景）</span>'
                    html += f'''
                        <div class="image-card">
                            <img src="data:image/png;base64,{img_data.get("base64", "")}" onclick="openLightbox(this)" alt="{img_info["name"]}">
                            <div class="image-info">
                                <h4>{img_info["name"]}</h4>
                                <p class="prompt">{img_info["prompt"]}</p>
                                <div class="fields">{fields_html}</div>
                            </div>
                        </div>'''
                html += '''</div></div>'''
            if tc.get("expected"):
                html += f'''<div class="info-row"><span class="info-label">预期结果</span><span class="info-value">{tc["expected"]}</span></div>'''
            if tc.get("verify"):
                html += f'''<div class="info-row"><span class="info-label">验证点</span><span class="info-value">{tc["verify"]}</span></div>'''
            html += '''
                </div>
            </div>
'''
        html += '''
        </div>
    </div>
'''

    # Lightbox HTML
    html += '''
    <div class="lightbox" onclick="closeLightbox()">
        <img src="" alt="">
        <div class="lightbox-info"></div>
    </div>
</div>

<script>
function toggleModule(header) {
    const content = header.nextElementSibling;
    const toggle = header.querySelector('.toggle');
    content.classList.toggle('show');
    toggle.style.transform = content.classList.contains('show') ? 'rotate(180deg)' : '';
}

function toggleTestCase(header) {
    const content = header.nextElementSibling;
    content.classList.toggle('show');
}

function openLightbox(img) {
    event.stopPropagation();
    const lightbox = document.querySelector('.lightbox');
    const lightboxImg = lightbox.querySelector('img');
    const lightboxInfo = lightbox.querySelector('.lightbox-info');
    lightboxImg.src = img.src;
    lightboxInfo.textContent = img.alt;
    lightbox.classList.add('show');
}

function closeLightbox() {
    document.querySelector('.lightbox').classList.remove('show');
}

// 默认展开第一个模块
document.querySelector('.module-header').click();
</script>
</body>
</html>'''

    return html

def main():
    print("=" * 60)
    print("生成HTML脑图（含测试数据图片）")
    print("=" * 60)

    # 生成HTML
    html = generate_html_mindmap()
    html_path = os.path.join(OUTPUT_ROOT, "公证智能体四期测试功能点_含图片.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML脑图已生成: {html_path}")

    # 同时生成图片文件夹
    test_data = get_test_data()
    for module_data in test_data:
        module_name = module_data["module"].replace(".", "_").replace(" ", "_")
        module_dir = os.path.join(OUTPUT_ROOT, module_name, "test_data")
        os.makedirs(module_dir, exist_ok=True)

        for tc in module_data["test_cases"]:
            for idx, img_info in enumerate(tc.get("images", [])):
                img = img_info["func"]()
                img_path = os.path.join(module_dir, f"{tc['id']}_{img_info['name']}.png")
                img.save(img_path)

                # 提示词
                prompt_path = img_path.replace(".png", "_提示词.md")
                with open(prompt_path, "w", encoding="utf-8") as f:
                    f.write(f"# {img_info['name']}\n\n")
                    f.write(f"**测试用例**: {tc['id']} - {tc['name']}\n\n")
                    f.write(f"**类型**: {tc['type']}\n\n")
                    f.write(f"## 图片说明\n\n{img_info['prompt']}\n\n")
                    if img_info.get("fields"):
                        f.write(f"## 关键字段\n\n")
                        for field in img_info["fields"]:
                            f.write(f"- {field}\n")

    print(f"\n图片文件夹已生成: {OUTPUT_ROOT}/各模块/test_data/")
    print("\n" + "=" * 60)
    print("完成！请打开HTML文件查看：")
    print(html_path)
    print("=" * 60)

if __name__ == "__main__":
    main()
