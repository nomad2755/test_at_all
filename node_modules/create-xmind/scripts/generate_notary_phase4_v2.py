# -*- coding: utf-8 -*-
"""
生成公证智能体四期测试功能点XMind - 优化版
- 每个模块单独文件夹
- 测试图片对应测试用例
- 提示词文件在图片旁边
"""

import os
import sys
sys.path.insert(0, r"C:\Users\14031\.claude\skills\create-xmind\scripts")

from create_xmind import create_xmind
from PIL import Image, ImageDraw, ImageFont

# 字体配置
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"

def get_font(size=22):
    """获取字体"""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

# 输出根目录
OUTPUT_ROOT = r"C:\Users\14031\Desktop\公证智能体四期测试功能点"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ============================================================================
# 测试图片生成函数
# ============================================================================

def create_id_card_positive(output_path):
    """身份证正面 - 正常"""
    img = Image.new('RGB', (640, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    # 标题
    draw.text((180, 20), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font_title)

    # 证件内容区
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)

    # 左侧照片区域
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)
    draw.text((65, 200), "照片", fill=(150, 150, 150), font=font_normal)

    # 右侧文字信息
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

    img.save(output_path)


def create_id_card_expired(output_path):
    """身份证 - 已过期（负向测试）"""
    img = Image.new('RGB', (640, 400), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((180, 20), "中华人民共和国居民身份证", fill=(0, 0, 0), font=font_title)
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)

    # 左侧照片区域
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)
    draw.text((65, 200), "照片", fill=(150, 150, 150), font=font_normal)

    # 右侧信息 - 已过期
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
    draw.text((x + 80, y), "2015.01.01-2025.01.01", fill=(180, 0, 0), font=font_normal)  # 红色表示过期

    img.save(output_path)


def create_hukouben(output_path):
    """户口本"""
    img = Image.new('RGB', (640, 480), color=(248, 248, 248))
    draw = ImageDraw.Draw(img)

    font_title = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.text((200, 15), "中华人民共和国户口簿", fill=(0, 0, 0), font=font_title)

    # 表头
    headers = ["姓名", "与户主关系", "性别", "民族", "出生地", "籍贯"]
    x_start = 50
    x_pos = [x_start, x_start + 90, x_start + 200, x_start + 280, x_start + 360, x_start + 450]

    for i, (h, x) in enumerate(zip(headers, x_pos)):
        draw.text((x, 55), h, fill=(0, 0, 0), font=font_small)

    # 分割线
    y = 75
    draw.line([(40, y), (600, y)], fill=(150, 150, 150), width=1)

    # 数据行
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

    # 住址变更记录
    y += 30
    draw.text((50, y), "住址变更记录：", fill=(80, 80, 80), font=font_normal)
    y += 30
    draw.text((50, y), "2020-01-01  由 北京市朝阳区XX路1号 迁至 现址", fill=(0, 0, 0), font=font_small)

    img.save(output_path)


def create_birth_cert(output_path):
    """出生医学证明"""
    img = Image.new('RGB', (700, 500), color=(230, 245, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((180, 15), "出生医学证明", fill=(0, 80, 160), font=font_title)

    # 标题装饰线
    draw.rectangle([(30, 50), (670, 55)], fill=(0, 80, 160))

    # 编号
    draw.text((500, 65), "编号：K110101001", fill=(80, 80, 80), font=font_small)

    # 新生儿信息
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

    # 签发信息
    y = 350
    draw.rectangle([(30, y), (670, y+2)], fill=(0, 80, 160))
    y += 15
    draw.text((50, y), "签发机构：北京市海淀区妇幼保健院", fill=(80, 80, 80), font=font_small)
    draw.text((400, y), "签发日期：2016-03-28", fill=(80, 80, 80), font=font_small)

    img.save(output_path)


def create_business_license(output_path):
    """营业执照"""
    img = Image.new('RGB', (640, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(28)
    font_normal = get_font(18)
    font_small = get_font(14)

    # 红色标题栏
    draw.rectangle([(0, 0), (640, 50)], fill=(200, 30, 30))
    draw.text((220, 10), "营业执照", fill=(255, 255, 255), font=font_title)

    # 副本标记
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

    # 盖章区域
    draw.ellipse([(450, 320), (580, 430)], outline=(200, 30, 30), width=2)
    draw.text((460, 365), "年检", fill=(200, 30, 30), font=font_small)

    img.save(output_path)


def create_notary_cert(output_path):
    """公证员执业证"""
    img = Image.new('RGB', (600, 400), color=(245, 248, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    # 蓝色标题栏
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

    # 签发信息
    y = 320
    draw.rectangle([(30, y), (570, y+2)], fill=(30, 80, 160))
    y += 10
    draw.text((50, y), "司法行政机关", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "北京市司法局", fill=(0, 0, 0), font=font_normal)

    draw.text((350, y), "发证日期", fill=(80, 80, 80), font=font_small)
    draw.text((450, y), "2025-01-01", fill=(0, 0, 0), font=font_normal)

    img.save(output_path)


def create_work_proof(output_path):
    """任职证明"""
    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.text((200, 30), "任职证明", fill=(0, 0, 0), font=font_title)

    # 分割线
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

    # 单位信息
    y += 60
    draw.text((350, y), "北京市公证处", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((350, y), "（公章）", fill=(150, 150, 150), font=font_small)

    y += 40
    draw.text((350, y), "2025年01月10日", fill=(80, 80, 80), font=font_small)

    img.save(output_path)


def create_guardian_proof(output_path):
    """监护关系证明"""
    img = Image.new('RGB', (600, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.text((180, 20), "出生医学证明（监护关系）", fill=(0, 80, 160), font=font_title)

    # 分割线
    draw.rectangle([(30, 50), (570, 55)], fill=(0, 80, 160))

    y = 70
    draw.text((50, y), "新生儿姓名", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "王小明", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "性别", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "男", fill=(0, 0, 0), font=font_normal)

    draw.text((300, y), "出生时间", fill=(80, 80, 80), font=font_small)
    draw.text((400, y), "2016年03月26日", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "父亲姓名", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "王五", fill=(0, 0, 0), font=font_normal)

    draw.text((300, y), "母亲姓名", fill=(80, 80, 80), font=font_small)
    draw.text((400, y), "赵六", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.rectangle([(30, y), (570, y+2)], fill=(200, 200, 200))

    y += 20
    draw.text((50, y), "监护人信息", fill=(0, 80, 160), font=font_normal)

    y += 40
    draw.text((50, y), "监护人姓名", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "王五", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((50, y), "与被监护人关系", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "父亲", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((50, y), "身份证号", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "110101198501011234", fill=(0, 0, 0), font=font_normal)

    y += 35
    draw.text((50, y), "联系电话", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "13800138001", fill=(0, 0, 0), font=font_normal)

    # 签发信息
    y += 60
    draw.rectangle([(30, y), (570, y+2)], fill=(0, 80, 160))
    y += 15
    draw.text((50, y), "签发机构：北京市海淀区妇幼保健院", fill=(80, 80, 80), font=font_small)
    draw.text((380, y), "签发日期：2016-03-28", fill=(80, 80, 80), font=font_small)

    img.save(output_path)


def create_train_ticket(output_path):
    """火车票"""
    img = Image.new('RGB', (600, 280), color=(30, 80, 160))
    draw = ImageDraw.Draw(img)

    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)

    # 左侧蓝色区域
    draw.rectangle([(0, 0), (200, 280)], fill=(20, 60, 130))

    # 红色标题
    draw.rectangle([(20, 15), (580, 55)], fill=(200, 30, 30))
    draw.text((240, 20), "G", fill=(255, 255, 255), font=font_title)
    draw.text((290, 25), "高铁", fill=(255, 255, 255), font=font_normal)

    # 车站信息
    y = 70
    draw.text((30, y), "北京南", fill=(255, 255, 255), font=font_title)
    draw.text((30, y + 45), "↓", fill=(255, 255, 255), font=font_title)
    draw.text((30, y + 90), "上海虹桥", fill=(255, 255, 255), font=font_title)

    draw.text((180, y), "2026-04-03", fill=(255, 255, 255), font=font_small)
    draw.text((180, y + 25), "09:00开", fill=(255, 255, 255), font=font_normal)

    # 右侧白色区域
    y = 30
    draw.rectangle([(230, 0), (600, 280)], fill=(255, 255, 255))

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

    img.save(output_path)


def create_flight_ticket(output_path):
    """机票"""
    img = Image.new('RGB', (650, 320), color=(0, 100, 60))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(18)
    font_small = get_font(14)

    # 顶部标题
    draw.rectangle([(0, 0), (650, 50)], fill=(0, 80, 50))
    draw.text((30, 12), "中国国际航空公司", fill=(255, 255, 255), font=font_title)
    draw.text((500, 15), "电子客票行程单", fill=(255, 255, 255), font=font_normal)

    # 白色内容区
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

    img.save(output_path)


def create_hotel_order(output_path):
    """酒店订单"""
    img = Image.new('RGB', (600, 400), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    font_title = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)

    # 标题栏
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

    img.save(output_path)


def create_id_card_blurry(output_path):
    """模糊的身份证照片（负向测试）"""
    img = Image.new('RGB', (640, 400), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)

    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(16)

    # 添加噪点模拟模糊
    import random
    for _ in range(5000):
        x = random.randint(0, 639)
        y = random.randint(0, 399)
        brightness = random.randint(180, 220)
        draw.point((x, y), fill=(brightness, brightness, brightness))

    draw.text((180, 20), "中华人民共和国居民身份证", fill=(150, 150, 150), font=font_title)

    # 模糊的边框
    draw.rectangle([(30, 60), (610, 380)], outline=(180, 180, 180), width=2)

    # 照片区域
    draw.rectangle([(40, 70), (200, 370)], outline=(180, 180, 180), width=1)

    # 模糊的文字
    x, y = 220, 80
    draw.text((x, y), "姓名", fill=(150, 150, 150), font=font_small)
    draw.text((x + 80, y), "张?", fill=(150, 150, 150), font=font_normal)

    y += 40
    draw.text((x, y), "公民身份号码", fill=(150, 150, 150), font=font_small)
    draw.text((x + 130, y), "11010119900101????", fill=(150, 150, 150), font=font_normal)

    y += 40
    draw.text((x, y), "有效期", fill=(150, 150, 150), font=font_small)

    # 提示文字
    draw.text((180, 320), "[图片模糊，无法识别]", fill=(180, 0, 0), font=font_normal)

    img.save(output_path)


def create_landscape(output_path):
    """风景图片（负向测试用）"""
    img = Image.new('RGB', (600, 400), color=(135, 206, 235))
    draw = ImageDraw.Draw(img)

    # 模拟简单风景
    # 天空
    draw.rectangle([(0, 0), (600, 250)], fill=(135, 206, 235))

    # 白云
    draw.ellipse([(100, 50), (200, 120)], fill=(255, 255, 255))
    draw.ellipse([(150, 30), (280, 100)], fill=(255, 255, 255))
    draw.ellipse([(350, 60), (450, 130)], fill=(255, 255, 255))

    # 草地
    draw.rectangle([(0, 250), (600, 400)], fill=(34, 139, 34))

    # 树木
    draw.polygon([(100, 250), (130, 150), (160, 250)], fill=(0, 100, 0))
    draw.polygon([(400, 250), (450, 120), (500, 250)], fill=(0, 100, 0))

    # 山脉
    draw.polygon([(200, 250), (300, 80), (400, 250)], fill=(100, 100, 100))
    draw.polygon([(300, 250), (420, 100), (540, 250)], fill=(80, 80, 80))

    img.save(output_path)


def create_business_license_wrong_name(output_path):
    """营业执照 - 名称不一致（负向测试）"""
    img = Image.new('RGB', (640, 450), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = get_font(28)
    font_normal = get_font(18)
    font_small = get_font(14)

    # 红色标题栏
    draw.rectangle([(0, 0), (640, 50)], fill=(200, 30, 30))
    draw.text((220, 10), "营业执照", fill=(255, 255, 255), font=font_title)

    y = 70
    draw.text((50, y), "名称", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "北京科技有限公司", fill=(0, 0, 0), font=font_normal)  # 与执业证不一致

    y += 40
    draw.text((50, y), "法定代表人", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "李公证", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "统一社会信用代码", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "91110105MA01234X51", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "执业机构", fill=(80, 80, 80), font=font_small)
    draw.text((200, y), "北京市公证处", fill=(0, 0, 0), font=font_normal)

    img.save(output_path)


# ============================================================================
# 创建模块文件夹和测试数据
# ============================================================================

def create_module_structure():
    """创建模块文件夹结构"""

    modules = [
        {
            "id": "01_数据资产对接",
            "name": "数据资产对接",
            "test_cases": [
                {
                    "id": "DAT-01",
                    "name": "正常发起数据资产公证（单条记录）",
                    "positive": [
                        {
                            "name": "火车票",
                            "func": create_train_ticket,
                            "filename": "DAT-01_火车票.png",
                            "prompt": "G字头高铁票，蓝色背景，包含：北京南→上海虹桥，2026-04-03，09:00开，一等座，5车12A，票价¥933，身份证号110101199001011234"
                        }
                    ],
                    "negative": [
                        {
                            "name": "风景图片（无有效信息）",
                            "func": create_landscape,
                            "filename": "DAT-01_风景_负向.png",
                            "prompt": "风景图片，无票据、无证件，用于测试'未识别到有效资产信息'场景"
                        }
                    ]
                },
                {
                    "id": "DAT-02",
                    "name": "正常发起数据资产公证（多条记录）",
                    "positive": [
                        {
                            "name": "机票",
                            "func": create_flight_ticket,
                            "filename": "DAT-02_机票.png",
                            "prompt": "电子客票行程单，绿色背景，中国国际航空公司CA1234，北京→上海，2026-04-05，08:30起飞，10:45到达，公务舱，票价¥2180，身份证号110101199001011234"
                        },
                        {
                            "name": "酒店订单",
                            "func": create_hotel_order,
                            "filename": "DAT-02_酒店订单.png",
                            "prompt": "酒店订单确认单，北京国际饭店，2026-04-03入住，2026-04-05离店，豪华双床房，入住人张三，总价¥1296"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "DAT-03",
                    "name": "数据资产公证-机票类型识别",
                    "positive": [
                        {
                            "name": "机票行程单",
                            "func": create_flight_ticket,
                            "filename": "DAT-03_机票.png",
                            "prompt": "电子客票行程单，绿色背景，中国国际航空公司CA1234，北京首都机场→上海浦东机场，2026-04-05，公务舱"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "DAT-04",
                    "name": "数据资产公证-酒店订单识别",
                    "positive": [
                        {
                            "name": "酒店订单",
                            "func": create_hotel_order,
                            "filename": "DAT-04_酒店订单.png",
                            "prompt": "酒店订单确认单，北京国际饭店，2026-04-03入住，2026-04-05离店，豪华双床房"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "DAT-05",
                    "name": "上传不含有效信息的图片",
                    "positive": [],
                    "negative": [
                        {
                            "name": "风景图片",
                            "func": create_landscape,
                            "filename": "DAT-05_风景_负向.png",
                            "prompt": "风景图片，不含任何票据或证件信息"
                        }
                    ]
                },
                {
                    "id": "DAT-06",
                    "name": "上传与公证无关的材料",
                    "positive": [],
                    "negative": [
                        {
                            "name": "营业执照",
                            "func": create_business_license,
                            "filename": "DAT-06_营业执照_负向.png",
                            "prompt": "营业执照，北京数字科技有限公司，法定代表人钱七，用于测试'不支持该类型资产'场景"
                        }
                    ]
                }
            ]
        },
        {
            "id": "02_实名认证",
            "name": "实名认证",
            "test_cases": [
                {
                    "id": "AUTH-01",
                    "name": "正常上传身份证进行实名认证",
                    "positive": [
                        {
                            "name": "身份证正面",
                            "func": create_id_card_positive,
                            "filename": "AUTH-01_身份证正面.png",
                            "prompt": "中华人民共和国居民身份证，姓名张三，性别男，民族汉族，1990年01月01日出生，住址北京市朝阳区建国路88号，身份证号110101199001011234，有效期2025.01.01-2035.01.01"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AUTH-02",
                    "name": "身份证有效期校验（有效期内）",
                    "positive": [
                        {
                            "name": "有效期内的身份证",
                            "func": create_id_card_positive,
                            "filename": "AUTH-02_身份证_有效期内.png",
                            "prompt": "中华人民共和国居民身份证，有效期2025.01.01-2035.01.01，在有效期内"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AUTH-03",
                    "name": "实名认证-人像面识别",
                    "positive": [
                        {
                            "name": "身份证人像面",
                            "func": create_id_card_positive,
                            "filename": "AUTH-03_身份证_人像面.png",
                            "prompt": "身份证人像面，姓名张三，性别男，民族汉族，1990年01月01日出生"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AUTH-04",
                    "name": "实名认证-国徽面识别",
                    "positive": [
                        {
                            "name": "身份证国徽面",
                            "func": create_id_card_positive,
                            "filename": "AUTH-04_身份证_国徽面.png",
                            "prompt": "身份证国徽面，身份证号110101199001011234，签发机关北京市公安局朝阳分局，有效期2025.01.01-2035.01.01"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AUTH-05",
                    "name": "上传模糊的身份证照片",
                    "positive": [],
                    "negative": [
                        {
                            "name": "模糊的身份证",
                            "func": create_id_card_blurry,
                            "filename": "AUTH-05_身份证_模糊_负向.png",
                            "prompt": "模糊的身份证照片，字迹不清晰，用于测试OCR识别失败场景"
                        }
                    ]
                },
                {
                    "id": "AUTH-06",
                    "name": "上传非身份证图片",
                    "positive": [],
                    "negative": [
                        {
                            "name": "营业执照（非身份证）",
                            "func": create_business_license,
                            "filename": "AUTH-06_营业执照_负向.png",
                            "prompt": "营业执照，用于测试系统识别为非身份证并提示的场景"
                        }
                    ]
                },
                {
                    "id": "AUTH-07",
                    "name": "身份证有效期已过期",
                    "positive": [],
                    "negative": [
                        {
                            "name": "已过期的身份证",
                            "func": create_id_card_expired,
                            "filename": "AUTH-07_身份证_已过期_负向.png",
                            "prompt": "中华人民共和国居民身份证，姓名李四，有效期2015.01.01-2025.01.01（已过期），用于测试过期证件检测场景"
                        }
                    ]
                }
            ]
        },
        {
            "id": "03_公证员资质申请",
            "name": "公证员资质申请",
            "test_cases": [
                {
                    "id": "CERT-01",
                    "name": "正常提交公证员资质申请",
                    "positive": [
                        {
                            "name": "公证员执业证",
                            "func": create_notary_cert,
                            "filename": "CERT-01_公证员执业证.png",
                            "prompt": "公证员执业证，姓名李公证，执业证号3101010001，执业机构北京市公证处，执业类别公证业务，有效期2025年01月01日至2027年12月31日，身份证号110101198001011234"
                        },
                        {
                            "name": "任职证明",
                            "func": create_work_proof,
                            "filename": "CERT-01_任职证明.png",
                            "prompt": "任职证明，证明李公证于2020年01月起在北京市公证处工作，现任职务为公证员，加盖北京市公证处公章"
                        },
                        {
                            "name": "半身照",
                            "func": create_id_card_positive,
                            "filename": "CERT-01_半身照.png",
                            "prompt": "标准证件半身照，姓名张三，蓝色背景，正面照"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "CERT-02",
                    "name": "公证员执业证识别",
                    "positive": [
                        {
                            "name": "公证员执业证",
                            "func": create_notary_cert,
                            "filename": "CERT-02_公证员执业证.png",
                            "prompt": "公证员执业证，姓名李公证，执业证号3101010001，执业机构北京市公证处"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "CERT-03",
                    "name": "任职证明识别",
                    "positive": [
                        {
                            "name": "任职证明",
                            "func": create_work_proof,
                            "filename": "CERT-03_任职证明.png",
                            "prompt": "任职证明，证明李公证于2020年01月起在北京市公证处工作，现任职务为公证员"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "CERT-04",
                    "name": "半身照上传",
                    "positive": [
                        {
                            "name": "半身照",
                            "func": create_id_card_positive,
                            "filename": "CERT-04_半身照.png",
                            "prompt": "标准证件半身照，正面照，包含头部和肩部"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "CERT-05",
                    "name": "执业证与任职证明信息不一致",
                    "positive": [],
                    "negative": [
                        {
                            "name": "营业执照（名称不一致）",
                            "func": create_business_license_wrong_name,
                            "filename": "CERT-05_营业执照_名称不一致_负向.png",
                            "prompt": "营业执照，名称为北京科技有限公司，用于测试执业证与任职证明信息不一致的场景"
                        }
                    ]
                },
                {
                    "id": "CERT-06",
                    "name": "证件照片不完整",
                    "positive": [],
                    "negative": [
                        {
                            "name": "模糊的执业证",
                            "func": create_id_card_blurry,
                            "filename": "CERT-06_执业证_残缺_负向.png",
                            "prompt": "残缺的公证员执业证照片，证件信息不完整，用于测试不完整证件检测场景"
                        }
                    ]
                }
            ]
        },
        {
            "id": "04_流程优化",
            "name": "流程优化",
            "test_cases": [
                {
                    "id": "FLOW-01",
                    "name": "申办人信息合并填写",
                    "positive": [
                        {
                            "name": "身份证（信息回显）",
                            "func": create_id_card_positive,
                            "filename": "FLOW-01_身份证.png",
                            "prompt": "身份证信息，用于自动回显申办人信息：姓名张三，电话13800138001，住址北京市朝阳区建国路88号"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "FLOW-02",
                    "name": "AI公证员接待-历史消息调整",
                    "positive": [],
                    "negative": []
                },
                {
                    "id": "FLOW-03",
                    "name": "智能生成文书-编辑功能",
                    "positive": [],
                    "negative": []
                }
            ]
        },
        {
            "id": "05_智能公证",
            "name": "智能公证",
            "test_cases": [
                {
                    "id": "AI-01",
                    "name": "AI公证员智能接待-正常对话",
                    "positive": [],
                    "negative": []
                },
                {
                    "id": "AI-02",
                    "name": "拍照上传材料",
                    "positive": [
                        {
                            "name": "身份证（拍照素材）",
                            "func": create_id_card_positive,
                            "filename": "AI-02_身份证_拍照素材.png",
                            "prompt": "身份证正面照，清晰度高，用于拍照上传测试"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AI-03",
                    "name": "相册选择上传",
                    "positive": [
                        {
                            "name": "相册素材-户口本",
                            "func": create_hukouben,
                            "filename": "AI-03_户口本_相册素材.png",
                            "prompt": "中华人民共和国户口簿，包含户主李四、之子张三、之女王芳的完整信息"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AI-04",
                    "name": "文件上传",
                    "positive": [
                        {
                            "name": "出生医学证明",
                            "func": create_birth_cert,
                            "filename": "AI-04_出生医学证明.png",
                            "prompt": "出生医学证明，新生儿王小明，男，2016年03月26日出生，出生地北京市海淀区妇幼保健院，父亲王五，母亲赵六"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AI-05",
                    "name": "申办人信息自动回显",
                    "positive": [
                        {
                            "name": "身份证（信息回显）",
                            "func": create_id_card_positive,
                            "filename": "AI-05_身份证.png",
                            "prompt": "身份证信息，姓名张三，身份证号110101199001011234，用于测试信息自动回显"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AI-06",
                    "name": "多材料连续上传",
                    "positive": [
                        {
                            "name": "身份证+户口本+出生证明组合",
                            "func": create_id_card_positive,
                            "filename": "AI-06_身份证.png",
                            "prompt": "材料1：身份证"
                        },
                        {
                            "name": "户口本",
                            "func": create_hukouben,
                            "filename": "AI-06_户口本.png",
                            "prompt": "材料2：户口本"
                        },
                        {
                            "name": "出生医学证明",
                            "func": create_birth_cert,
                            "filename": "AI-06_出生医学证明.png",
                            "prompt": "材料3：出生医学证明"
                        }
                    ],
                    "negative": []
                },
                {
                    "id": "AI-07",
                    "name": "AI材料智能分类",
                    "positive": [
                        {
                            "name": "混合材料截图",
                            "func": create_id_card_positive,
                            "filename": "AI-07_混合材料.png",
                            "prompt": "混合材料截图，包含身份证、火车票、营业执照等多种类型，用于测试AI智能分类功能"
                        }
                    ],
                    "negative": []
                }
            ]
        }
    ]

    return modules


def generate_all_images_and_prompts():
    """生成所有图片和提示词"""
    modules = create_module_structure()

    all_readme_content = []
    total_images = 0

    for module in modules:
        module_dir = os.path.join(OUTPUT_ROOT, module["id"])
        test_data_dir = os.path.join(module_dir, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)

        module_readme = []
        module_readme.append(f"# {module['name']} - 测试数据清单")
        module_readme.append("")
        module_readme.append(f"模块ID: {module['id']}")
        module_readme.append("")

        for tc in module["test_cases"]:
            if tc["positive"] or tc["negative"]:
                module_readme.append(f"## {tc['id']}：{tc['name']}")
                module_readme.append("")

                # 正向测试
                if tc["positive"]:
                    module_readme.append("### 正向测试数据")
                    for item in tc["positive"]:
                        img_path = os.path.join(test_data_dir, item["filename"])
                        item["func"](img_path)

                        # 生成提示词文件
                        prompt_path = img_path.replace(".png", "_提示词.md")
                        with open(prompt_path, "w", encoding="utf-8") as f:
                            f.write(f"# {item['name']}\n\n")
                            f.write(f"**对应测试用例**: {tc['id']}：{tc['name']}\n\n")
                            f.write(f"**文件名**: {item['filename']}\n\n")
                            f.write(f"**测试数据类型**: 正向\n\n")
                            f.write(f"## 图片说明\n\n")
                            f.write(f"{item['prompt']}\n\n")
                            f.write(f"## 必须保留的文字内容\n\n")
                            # 提取关键字段
                            fields = []
                            if "身份证" in item["name"] or "身份证" in item["prompt"]:
                                fields = ["姓名", "性别", "民族", "出生", "住址", "公民身份号码", "签发机关", "有效期", "110101199001011234"]
                            elif "火车票" in item["name"] or "G" in item["prompt"]:
                                fields = ["G1234", "北京南", "上海虹桥", "2026-04-03", "09:00", "一等座", "5车12A", "¥933", "110101199001011234"]
                            elif "机票" in item["name"] or "CA" in item["prompt"]:
                                fields = ["CA1234", "北京首都机场", "上海浦东机场", "08:30", "10:45", "公务舱", "¥2180", "110101199001011234"]
                            elif "酒店" in item["name"]:
                                fields = ["北京国际饭店", "2026-04-03", "2026-04-05", "豪华双床房", "¥1296", "张三"]
                            elif "执业证" in item["name"]:
                                fields = ["李公证", "3101010001", "北京市公证处", "公证业务", "2025年01月01日", "2027年12月31日", "110101198001011234"]
                            elif "任职" in item["name"]:
                                fields = ["李公证", "110101198001011234", "2020年01月", "公证员", "北京市公证处", "公章"]
                            elif "户口" in item["name"]:
                                fields = ["李四", "户主", "之子", "之女", "汉族", "北京市"]
                            elif "出生" in item["name"]:
                                fields = ["王小明", "男", "2016年03月26日", "王五", "赵六", "110101198501011234", "110101198801015678", "北京市海淀区妇幼保健院"]
                            elif "营业" in item["name"]:
                                fields = ["91110105MA01234X51", "北京数字科技有限公司", "钱七", "2020年01月15日"]
                            elif "半身" in item["name"]:
                                fields = ["张三"]

                            for field in fields:
                                module_readme.append(f"- {field}")
                            module_readme.append("")
                            module_readme.append(f"## AI增强提示词（英文）\n\n")
                            module_readme.append(f"```\n{item['prompt']}\n```\n")

                        module_readme.append(f"| {item['filename']} | 正向 | [提示词](test_data/{item['filename'].replace('.png', '_提示词.md')}) |\n")
                        total_images += 1

                # 负向测试
                if tc["negative"]:
                    module_readme.append("### 负向测试数据")
                    for item in tc["negative"]:
                        img_path = os.path.join(test_data_dir, item["filename"])
                        item["func"](img_path)

                        # 生成提示词文件
                        prompt_path = img_path.replace(".png", "_提示词.md")
                        with open(prompt_path, "w", encoding="utf-8") as f:
                            f.write(f"# {item['name']}\n\n")
                            f.write(f"**对应测试用例**: {tc['id']}：{tc['name']}\n\n")
                            f.write(f"**文件名**: {item['filename']}\n\n")
                            f.write(f"**测试数据类型**: 负向\n\n")
                            f.write(f"## 图片说明\n\n")
                            f.write(f"{item['prompt']}\n\n")

                        module_readme.append(f"| {item['filename']} | 负向 | [提示词](test_data/{item['filename'].replace('.png', '_提示词.md')}) |\n")
                        total_images += 1

                module_readme.append("")

        # 保存模块README
        readme_path = os.path.join(module_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("\n".join(module_readme))

        all_readme_content.extend(module_readme)

    # 生成汇总README
    summary_path = os.path.join(OUTPUT_ROOT, "测试数据清单汇总.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# 公证智能体四期测试功能点 - 测试数据清单汇总\n\n")
        f.write("生成时间：2026-04-03\n\n")
        f.write("---\n\n")
        f.write("## 文件夹结构\n\n")
        f.write("```\n公证智能体四期测试功能点/\n├── 公证智能体四期测试功能点_详细版.xmind\n├── 测试数据清单汇总.md\n")
        for module in modules:
            f.write(f"├── {module['id']}/\n")
            f.write(f"│   ├── README.md\n")
            f.write(f"│   └── test_data/\n")
        f.write("```\n\n")
        f.write("---\n\n")
        f.write("## 各模块测试数据\n\n")
        for module in modules:
            f.write(f"### {module['id']} - {module['name']}\n\n")
            tc_count = len([tc for tc in module["test_cases"] if tc["positive"] or tc["negative"]])
            img_count = sum(len(tc["positive"]) + len(tc["negative"]) for tc in module["test_cases"])
            f.write(f"- 测试用例数：{tc_count}\n")
            f.write(f"- 测试图片数：{img_count}\n")
            f.write(f"- 详细说明：[查看]({module['id']}/README.md)\n\n")

    print(f"\n完成！生成统计：")
    print(f"- 模块数：{len(modules)}")
    print(f"- 测试图片总数：{total_images}")
    print(f"- 输出目录：{OUTPUT_ROOT}")

    return OUTPUT_ROOT


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 60)
    print("公证智能体四期测试功能点生成")
    print("=" * 60)

    # Step 1: 生成XMind
    print("\n[Step 1] 生成XMind脑图...")

    data = {
        "root_title": "公证智能体APP端（四期）测试功能点",
        "sheet_title": "测试功能点",
        "branches": [
            {
                "title": "1. 数据资产对接",
                "children": [
                    {
                        "title": "1.1 功能描述",
                        "children": [
                            "数据资产公证发起",
                            "支持上传数据资产列表截图",
                            "AI自动识别数据类型（火车票、机票、酒店订单等）",
                            "生成材料清单供用户确认"
                        ]
                    },
                    {
                        "title": "1.2 正向测试用例",
                        "children": [
                            {
                                "title": "DAT-01：正常发起数据资产公证（单条记录）",
                                "children": [
                                    "前置条件：企业账号已认证、个人账号已登录",
                                    "操作步骤：1.登录APP 2.进入数据资产对接页面 3.点击'发起数据资产公证' 4.上传数据资产列表截图 5.等待AI识别",
                                    "测试数据：单张火车票截图",
                                    "测试图片：[01_数据资产对接/test_data/DAT-01_火车票.png]",
                                    "预期结果：AI成功识别数据类型，显示'火车票'标签，生成材料清单",
                                    "验证点：1.申办人信息自动回显 2.材料清单显示正确 3.可进入下一步"
                                ]
                            },
                            {
                                "title": "DAT-02：正常发起数据资产公证（多条记录）",
                                "children": [
                                    "前置条件：企业账号已认证、个人账号已登录",
                                    "操作步骤：1.进入数据资产公证页面 2.上传包含多条记录的截图 3.等待AI批量识别",
                                    "测试数据：机票截图、酒店订单截图",
                                    "测试图片：[01_数据资产对接/test_data/DAT-02_机票.png]、[01_数据资产对接/test_data/DAT-02_酒店订单.png]",
                                    "预期结果：AI识别出多条记录，材料清单显示全部记录",
                                    "验证点：1.多条记录全部识别 2.每条记录信息完整"
                                ]
                            },
                            {
                                "title": "DAT-03：数据资产公证-机票类型识别",
                                "children": [
                                    "前置条件：个人账号已登录",
                                    "测试数据：电子客票行程单",
                                    "测试图片：[01_数据资产对接/test_data/DAT-03_机票.png]",
                                    "预期结果：识别为'机票'类型，显示航班详情"
                                ]
                            },
                            {
                                "title": "DAT-04：数据资产公证-酒店订单识别",
                                "children": [
                                    "前置条件：个人账号已登录",
                                    "测试数据：酒店订单截图",
                                    "测试图片：[01_数据资产对接/test_data/DAT-04_酒店订单.png]",
                                    "预期结果：识别为'酒店订单'类型，显示酒店详情"
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
                                    "测试数据：风景图片",
                                    "测试图片：[01_数据资产对接/test_data/DAT-05_风景_负向.png]",
                                    "预期结果：AI无法识别，提示'未识别到有效资产信息'",
                                    "提示词：[01_数据资产对接/test_data/DAT-05_风景_负向_提示词.md]"
                                ]
                            },
                            {
                                "title": "DAT-06：上传与公证无关的材料",
                                "children": [
                                    "前置条件：个人账号已登录",
                                    "测试数据：营业执照图片",
                                    "测试图片：[01_数据资产对接/test_data/DAT-06_营业执照_负向.png]",
                                    "预期结果：提示'不支持该类型资产'"
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "2. 实名认证",
                "children": [
                    {
                        "title": "2.1 功能描述",
                        "children": [
                            "个人实名认证",
                            "上传身份证照片进行OCR识别",
                            "验证身份信息真实性"
                        ]
                    },
                    {
                        "title": "2.2 正向测试用例",
                        "children": [
                            {
                                "title": "AUTH-01：正常上传身份证进行实名认证",
                                "children": [
                                    "前置条件：个人账号已登录、未认证",
                                    "操作步骤：1.进入实名认证页面 2.点击'上传身份证' 3.拍摄/选择身份证照片 4.提交认证",
                                    "测试数据：清晰的身份证照片（正面）",
                                    "测试图片：[02_实名认证/test_data/AUTH-01_身份证正面.png]",
                                    "预期结果：OCR成功识别，显示身份证信息",
                                    "提示词：[02_实名认证/test_data/AUTH-01_身份证正面_提示词.md]"
                                ]
                            },
                            {
                                "title": "AUTH-02：身份证有效期校验（有效期内）",
                                "children": [
                                    "测试数据：有效期至2025.01.01-2035.01.01的身份证",
                                    "测试图片：[02_实名认证/test_data/AUTH-02_身份证_有效期内.png]"
                                ]
                            },
                            {
                                "title": "AUTH-03：实名认证-人像面识别",
                                "children": [
                                    "测试数据：身份证人像面",
                                    "测试图片：[02_实名认证/test_data/AUTH-03_身份证_人像面.png]"
                                ]
                            },
                            {
                                "title": "AUTH-04：实名认证-国徽面识别",
                                "children": [
                                    "测试数据：身份证国徽面",
                                    "测试图片：[02_实名认证/test_data/AUTH-04_身份证_国徽面.png]"
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
                                    "测试数据：模糊的身份证照片",
                                    "测试图片：[02_实名认证/test_data/AUTH-05_身份证_模糊_负向.png]",
                                    "预期结果：提示'身份证照片不清晰，请重新拍摄'"
                                ]
                            },
                            {
                                "title": "AUTH-06：上传非身份证图片",
                                "children": [
                                    "测试数据：营业执照图片",
                                    "测试图片：[02_实名认证/test_data/AUTH-06_营业执照_负向.png]",
                                    "预期结果：提示'请上传身份证照片'"
                                ]
                            },
                            {
                                "title": "AUTH-07：身份证有效期已过期",
                                "children": [
                                    "测试数据：有效期至2020.01.01-2030.01.01的身份证",
                                    "测试图片：[02_实名认证/test_data/AUTH-07_身份证_已过期_负向.png]",
                                    "预期结果：提示'身份证已过期，请上传有效证件'"
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "3. 公证员资质申请",
                "children": [
                    {
                        "title": "3.1 功能描述",
                        "children": [
                            "公证员资质认证",
                            "上传公证员执业证、任职证明、半身照",
                            "提交资质审核"
                        ]
                    },
                    {
                        "title": "3.2 正向测试用例",
                        "children": [
                            {
                                "title": "CERT-01：正常提交公证员资质申请",
                                "children": [
                                    "前置条件：个人账号已登录、公证员角色",
                                    "操作步骤：1.进入公证员资质申请页面 2.上传公证员执业证 3.上传任职证明 4.上传半身照 5.提交申请",
                                    "测试数据：公证员执业证、任职证明（单位公章）、个人半身照",
                                    "测试图片：[03_公证员资质申请/test_data/CERT-01_公证员执业证.png]",
                                    "测试图片：[03_公证员资质申请/test_data/CERT-01_任职证明.png]",
                                    "测试图片：[03_公证员资质申请/test_data/CERT-01_半身照.png]"
                                ]
                            },
                            {
                                "title": "CERT-02：公证员执业证识别",
                                "children": [
                                    "测试图片：[03_公证员资质申请/test_data/CERT-02_公证员执业证.png]"
                                ]
                            },
                            {
                                "title": "CERT-03：任职证明识别",
                                "children": [
                                    "测试图片：[03_公证员资质申请/test_data/CERT-03_任职证明.png]"
                                ]
                            },
                            {
                                "title": "CERT-04：半身照上传",
                                "children": [
                                    "测试图片：[03_公证员资质申请/test_data/CERT-04_半身照.png]"
                                ]
                            }
                        ]
                    },
                    {
                        "title": "3.3 负向测试用例",
                        "children": [
                            {
                                "title": "CERT-05：执业证与任职证明信息不一致",
                                "children": [
                                    "测试数据：营业执照（名称不一致）",
                                    "测试图片：[03_公证员资质申请/test_data/CERT-05_营业执照_名称不一致_负向.png]"
                                ]
                            },
                            {
                                "title": "CERT-06：证件照片不完整",
                                "children": [
                                    "测试数据：残缺的公证员执业证照片",
                                    "测试图片：[03_公证员资质申请/test_data/CERT-06_执业证_残缺_负向.png]"
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "4. 流程优化",
                "children": [
                    {
                        "title": "4.1 功能描述",
                        "children": [
                            "申办人信息填写优化（步骤1+2合并）",
                            "AI公证员接待-历史消息可调整",
                            "智能生成文书-可修改编辑"
                        ]
                    },
                    {
                        "title": "4.2 正向测试用例",
                        "children": [
                            {
                                "title": "FLOW-01：申办人信息合并填写",
                                "children": [
                                    "测试数据：身份证照片（用于信息自动回显）",
                                    "测试图片：[04_流程优化/test_data/FLOW-01_身份证.png]"
                                ]
                            },
                            {
                                "title": "FLOW-02：AI公证员接待-历史消息调整"
                            },
                            {
                                "title": "FLOW-03：智能生成文书-编辑功能"
                            }
                        ]
                    }
                ]
            },
            {
                "title": "5. 智能公证",
                "children": [
                    {
                        "title": "5.1 功能描述",
                        "children": [
                            "AI公证员智能接待",
                            "多种材料上传方式（拍照、相册、文件）",
                            "申办人信息自动回显",
                            "智能材料识别与分类"
                        ]
                    },
                    {
                        "title": "5.2 正向测试用例",
                        "children": [
                            {
                                "title": "AI-01：AI公证员智能接待-正常对话"
                            },
                            {
                                "title": "AI-02：拍照上传材料",
                                "children": [
                                    "测试数据：身份证照片",
                                    "测试图片：[05_智能公证/test_data/AI-02_身份证_拍照素材.png]"
                                ]
                            },
                            {
                                "title": "AI-03：相册选择上传",
                                "children": [
                                    "测试数据：户口本照片",
                                    "测试图片：[05_智能公证/test_data/AI-03_户口本_相册素材.png]"
                                ]
                            },
                            {
                                "title": "AI-04：文件上传",
                                "children": [
                                    "测试数据：出生医学证明（PDF）",
                                    "测试图片：[05_智能公证/test_data/AI-04_出生医学证明.png]"
                                ]
                            },
                            {
                                "title": "AI-05：申办人信息自动回显",
                                "children": [
                                    "测试数据：身份证照片",
                                    "测试图片：[05_智能公证/test_data/AI-05_身份证.png]"
                                ]
                            },
                            {
                                "title": "AI-06：多材料连续上传",
                                "children": [
                                    "测试数据：身份证+户口本+出生医学证明",
                                    "测试图片：[05_智能公证/test_data/AI-06_身份证.png]",
                                    "测试图片：[05_智能公证/test_data/AI-06_户口本.png]",
                                    "测试图片：[05_智能公证/test_data/AI-06_出生医学证明.png]"
                                ]
                            },
                            {
                                "title": "AI-07：AI材料智能分类",
                                "children": [
                                    "测试数据：混合类型材料截图",
                                    "测试图片：[05_智能公证/test_data/AI-07_混合材料.png]"
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "title": "6. 测试数据清单",
                "children": [
                    {
                        "title": "6.1 证件类测试数据",
                        "children": [
                            "身份证照片（正面+反面）",
                            "户口本主页和个人页",
                            "公证员执业证",
                            "任职证明（带公章）",
                            "半身照（标准证件照）"
                        ]
                    },
                    {
                        "title": "6.2 票据类测试数据",
                        "children": [
                            "火车票（蓝色G/D车次）",
                            "机票（电子客票行程单）",
                            "酒店订单确认单",
                            "打车发票"
                        ]
                    },
                    {
                        "title": "6.3 文档类测试数据",
                        "children": [
                            "学历证明文件",
                            "营业执照",
                            "出生医学证明",
                            "婚姻状况证明"
                        ]
                    }
                ]
            },
            {
                "title": "7. 特殊场景测试",
                "children": [
                    {
                        "title": "7.1 兼容性测试",
                        "children": [
                            "不同手机分辨率适配（1080P/2K/4K）",
                            "不同Android版本兼容（Android 10/11/12/13）",
                            "不同iOS版本兼容（iOS 14/15/16/17）"
                        ]
                    },
                    {
                        "title": "7.2 性能测试",
                        "children": [
                            "OCR识别响应时间（应在3秒内）",
                            "大文件上传速度测试",
                            "连续操作内存占用"
                        ]
                    },
                    {
                        "title": "7.3 安全测试",
                        "children": [
                            "敏感信息传输加密验证",
                            "身份认证Token有效性",
                            "会话超时自动退出"
                        ]
                    }
                ]
            },
            {
                "title": "8. 风险项与关注点",
                "children": [
                    {
                        "title": "8.1 高风险项",
                        "children": [
                            "实名认证-身份证信息识别准确性（涉及法律效力）",
                            "公证员资质申请-三证信息一致性校验",
                            "智能公证-材料真实性核验"
                        ]
                    },
                    {
                        "title": "8.2 中风险项",
                        "children": [
                            "AI对话-敏感词过滤机制",
                            "材料上传-文件安全校验",
                            "流程优化-数据回显准确性"
                        ]
                    },
                    {
                        "title": "8.3 需重点关注",
                        "children": [
                            "用户体验：OCR识别失败后的引导",
                            "异常处理：网络波动时的数据保护",
                            "合规要求：个人信息保护法相关"
                        ]
                    }
                ]
            }
        ]
    }

    xmind_path = os.path.join(OUTPUT_ROOT, "公证智能体四期测试功能点_详细版.xmind")
    create_xmind(data, xmind_path)

    # Step 2: 生成测试图片和提示词
    print("\n[Step 2] 生成测试图片和提示词...")
    root_dir = generate_all_images_and_prompts()

    print("\n" + "=" * 60)
    print("全部生成完成！")
    print("=" * 60)
    print(f"\n输出目录：{OUTPUT_ROOT}")
    print(f"\n文件夹结构：")
    print(f"公证智能体四期测试功能点/")
    print(f"├── 公证智能体四期测试功能点_详细版.xmind    # XMind脑图")
    print(f"├── 测试数据清单汇总.md                    # 测试数据总览")
    print(f"├── 01_数据资产对接/")
    print(f"│   ├── README.md                         # 模块说明")
    print(f"│   └── test_data/")
    print(f"│       ├── DAT-01_火车票.png")
    print(f"│       ├── DAT-01_火车票_提示词.md")
    print(f"│       └── ...")
    print(f"├── 02_实名认证/")
    print(f"│   └── ...")
    print(f"├── 03_公证员资质申请/")
    print(f"│   └── ...")
    print(f"├── 04_流程优化/")
    print(f"│   └── ...")
    print(f"└── 05_智能公证/")
    print(f"    └── ...")


if __name__ == "__main__":
    main()
