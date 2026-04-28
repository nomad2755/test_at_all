# -*- coding: utf-8 -*-
"""
测试数据图片生成脚本

根据测试用例需求生成用于 OCR 识别测试的图片。

使用方式：
    # 生成所有测试数据图片
    python generate_test_images.py

    # 生成指定类型图片
    python generate_test_images.py --type id_card --output test_data/

    # 查看支持的图片类型
    python generate_test_images.py --list

依赖：
    pip install Pillow
"""

import os
import argparse
from PIL import Image, ImageDraw, ImageFont

# 字体配置（Windows）
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑

def get_font(size=22):
    """获取字体"""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

def create_id_card(output_path):
    """生成身份证图片"""
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
    print(f"[OK] {output_path}")


def create_hukouben(output_path):
    """生成户口本图片"""
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
    print(f"[OK] {output_path}")


def create_birth_cert(output_path):
    """生成出生医学证明"""
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
    print(f"[OK] {output_path}")


def create_business_license(output_path):
    """生成营业执照"""
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
    print(f"[OK] {output_path}")


def create_notary_cert(output_path):
    """生成公证员执业证"""
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
    print(f"[OK] {output_path}")


def create_work_proof(output_path):
    """生成任职证明"""
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
    print(f"[OK] {output_path}")


def create_guardian_proof(output_path):
    """生成监护关系证明"""
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
    print(f"[OK] {output_path}")


# 图片类型映射
IMAGE_TYPES = {
    "id_card": create_id_card,
    "hukouben": create_hukouben,
    "birth_cert": create_birth_cert,
    "business_license": create_business_license,
    "notary_cert": create_notary_cert,
    "work_proof": create_work_proof,
    "guardian_proof": create_guardian_proof,
}

IMAGE_NAMES = {
    "id_card": "01_身份证.png",
    "hukouben": "02_户口本.png",
    "birth_cert": "03_出生医学证明.png",
    "business_license": "04_营业执照.png",
    "notary_cert": "05_公证员执业证.png",
    "work_proof": "06_任职证明.png",
    "guardian_proof": "07_监护关系证明.png",
}


def main():
    parser = argparse.ArgumentParser(description="生成测试数据图片")
    parser.add_argument("--type", "-t", choices=list(IMAGE_TYPES.keys()), help="指定图片类型")
    parser.add_argument("--output", "-o", default="test_data", help="输出目录")
    parser.add_argument("--list", "-l", action="store_true", help="列出支持的图片类型")

    args = parser.parse_args()

    if args.list:
        print("支持的图片类型：")
        for key, name in IMAGE_NAMES.items():
            print(f"  {key:20s} -> {name}")
        return

    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)

    if args.type:
        # 生成指定类型
        func = IMAGE_TYPES[args.type]
        name = IMAGE_NAMES[args.type]
        path = os.path.join(args.output, name)
        func(path)
    else:
        # 生成所有类型
        print(f"生成测试数据图片到: {args.output}/")
        print("-" * 40)
        for key, func in IMAGE_TYPES.items():
            name = IMAGE_NAMES[key]
            path = os.path.join(args.output, name)
            func(path)
        print("-" * 40)
        print(f"完成！共生成 {len(IMAGE_TYPES)} 张图片")


if __name__ == "__main__":
    main()
