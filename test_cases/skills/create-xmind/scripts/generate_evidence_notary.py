# -*- coding: utf-8 -*-
"""
存证转公证流程图 - 测试功能点生成
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
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()

OUTPUT_ROOT = r"C:\Users\14031\Desktop\存证转公证流程图"
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

def create_notary_matters_form():
    """公证事项申请表"""
    img = Image.new('RGB', (700, 500), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)

    draw.rectangle([(0, 0), (700, 60)], fill=(0, 80, 160))
    draw.text((200, 15), "公证事项申请表", fill=(255, 255, 255), font=font_title)

    y = 80
    draw.text((50, y), "申请人姓名", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "张三", fill=(0, 0, 0), font=font_normal)

    draw.text((350, y), "联系电话", fill=(80, 80, 80), font=font_small)
    draw.text((480, y), "13800138001", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "身份证号", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "110101199001011234", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((50, y), "公证事项类型", fill=(80, 80, 80), font=font_small)
    draw.rectangle([(180, y-5), (400, y+25)], outline=(0, 80, 160), width=2)
    draw.text((185, y), "委托公证", fill=(0, 80, 160), font=font_normal)

    y += 50
    draw.text((50, y), "公证事项描述", fill=(80, 80, 80), font=font_small)
    draw.rectangle([(180, y-5), (650, y+80)], outline=(180, 180, 180), width=1)
    draw.text((185, y+5), "委托办理房产过户手续，", fill=(0, 0, 0), font=font_normal)
    draw.text((185, y+30), "涉及金额50万元。", fill=(0, 0, 0), font=font_normal)

    y += 100
    draw.text((50, y), "申请日期", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "2026-04-03", fill=(0, 0, 0), font=font_normal)

    draw.text((400, y), "申请人签字", fill=(80, 80, 80), font=font_small)
    draw.line([(520, y), (620, y)], fill=(0, 0, 0), width=1)

    y += 60
    draw.rectangle([(250, y), (450, y+50)], fill=(0, 80, 160))
    draw.text((290, y+12), "提交申请", fill=(255, 255, 255), font=font_normal)

    return img

def create_commitment_letter():
    """告知承诺书"""
    img = Image.new('RGB', (700, 550), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(18)
    font_small = get_font(14)

    draw.text((250, 15), "告知承诺书", fill=(0, 0, 0), font=font_title)
    draw.line([(50, 50), (650, 50)], fill=(150, 150, 150), width=1)

    y = 70
    draw.text((50, y), "申请人张三（身份证号：110101199001011234）郑重承诺：", fill=(0, 0, 0), font=font_normal)
    y += 40
    draw.text((50, y), "1. 所提供的申请材料真实、合法、有效；", fill=(0, 0, 0), font=font_normal)
    y += 35
    draw.text((50, y), "2. 申请公证的事项系本人真实意思表示；", fill=(0, 0, 0), font=font_normal)
    y += 35
    draw.text((50, y), "3. 如有虚假，愿承担相应的法律责任。", fill=(0, 0, 0), font=font_normal)

    y += 80
    draw.text((50, y), "承诺人签字：", fill=(0, 0, 0), font=font_normal)
    draw.line([(180, y+5), (350, y+5)], fill=(0, 0, 0), width=1)

    y += 50
    draw.text((50, y), "日期：", fill=(0, 0, 0), font=font_normal)
    draw.text((120, y), "2026年04月03日", fill=(0, 0, 0), font=font_normal)

    draw.rectangle([(450, y-10), (650, y+40)], fill=(200, 30, 30))
    draw.text((500, y), "确认签字", fill=(255, 255, 255), font=font_normal)

    return img

def create_acceptance_form():
    """受理单"""
    img = Image.new('RGB', (650, 480), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(26)
    font_normal = get_font(20)
    font_small = get_font(14)

    draw.rectangle([(0, 0), (650, 50)], fill=(200, 30, 30))
    draw.text((240, 10), "公证受理单", fill=(255, 255, 255), font=font_title)

    y = 70
    draw.text((50, y), "受理编号", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "GZ2026040300123", fill=(0, 0, 0), font=font_normal)

    draw.text((350, y), "受理日期", fill=(80, 80, 80), font=font_small)
    draw.text((450, y), "2026-04-03", fill=(0, 0, 0), font=font_normal)

    y += 45
    draw.text((50, y), "申请人", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "张三", fill=(0, 0, 0), font=font_normal)

    draw.text((350, y), "公证事项", fill=(80, 80, 80), font=font_small)
    draw.text((450, y), "委托公证", fill=(0, 0, 0), font=font_normal)

    y += 45
    draw.text((50, y), "公证员", fill=(80, 80, 80), font=font_small)
    draw.text((150, y), "李公证", fill=(0, 0, 0), font=font_normal)

    draw.text((350, y), "预计完成", fill=(80, 80, 80), font=font_small)
    draw.text((450, y), "2026-04-10", fill=(0, 0, 0), font=font_normal)

    y += 60
    draw.rectangle([(30, y), (620, y+2)], fill=(200, 200, 200))
    y += 20

    draw.text((50, y), "申请材料清单：", fill=(0, 0, 0), font=font_normal)
    y += 35
    draw.text((80, y), "☑ 身份证原件及复印件", fill=(0, 100, 0), font=font_small)
    y += 25
    draw.text((80, y), "☑ 户口本原件", fill=(0, 100, 0), font=font_small)
    y += 25
    draw.text((80, y), "☑ 房产证原件", fill=(0, 100, 0), font=font_small)
    y += 25
    draw.text((80, y), "☑ 委托书", fill=(0, 100, 0), font=font_small)

    y += 60
    draw.rectangle([(30, y), (620, y+2)], fill=(200, 200, 200))
    y += 15
    draw.text((50, y), "公证员签字：", fill=(80, 80, 80), font=font_small)
    draw.line([(150, y+5), (280, y+5)], fill=(0, 0, 0), width=1)

    draw.text((350, y), "公证机构：", fill=(80, 80, 80), font=font_small)
    draw.text((470, y), "北京市公证处", fill=(0, 0, 0), font=font_small)

    return img

def create_certificate():
    """公证书"""
    img = Image.new('RGB', (700, 550), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(14)

    draw.rectangle([(0, 0), (700, 60)], fill=(200, 30, 30))
    draw.text((280, 15), "公证书", fill=(255, 255, 255), font=font_title)

    y = 80
    draw.text((50, y), "公证书编号", fill=(80, 80, 80), font=font_small)
    draw.text((180, y), "(2026)京公证字第1234号", fill=(0, 0, 0), font=font_normal)

    y += 50
    draw.text((250, y), "委托公证书", fill=(0, 0, 0), font=font_title)

    y += 60
    draw.text((50, y), "申请人：张三（身份证号：110101199001011234）", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "委托事项：委托办理位于北京市朝阳区房产过户手续", fill=(0, 0, 0), font=font_normal)

    y += 40
    draw.text((50, y), "受托人：李四（身份证号：110101198501011234）", fill=(0, 0, 0), font=font_normal)

    y += 60
    draw.text((50, y), "本公证书证明上述委托行为真实、合法、有效。", fill=(0, 0, 0), font=font_normal)

    y += 80
    draw.text((400, y), "公证员：李公证", fill=(0, 0, 0), font=font_normal)
    y += 35
    draw.text((400, y), "执业证号：3101010001", fill=(80, 80, 80), font=font_small)

    y += 50
    draw.text((400, y), "北京市公证处", fill=(0, 0, 0), font=font_normal)
    y += 35
    draw.text((400, y), "2026年04月08日", fill=(80, 80, 80), font=font_normal)

    draw.ellipse([(50, 350), (180, 420)], outline=(200, 30, 30), width=3)
    draw.text((65, 375), "公证", fill=(200, 30, 30), font=font_normal)
    draw.text((65, 400), "专用", fill=(200, 30, 30), font=font_small)

    return img

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# ============================================================================
# 测试数据定义（基于完整流程图）
# ============================================================================

def get_test_data():
    return [
        {
            "module": "1. 申办人发起申请",
            "test_cases": [
                {
                    "id": "FLOW-01", "name": "正常发起申请", "type": "正向",
                    "prerequisite": "申办人已登录",
                    "steps": "1.点击'发起申请' 2.填写公证事项表 3.提交申请",
                    "images": [
                        {"func": create_notary_matters_form, "name": "公证事项申请表", "prompt": "公证事项申请表，申请人张三，身份证号110101199001011234，公证事项类型委托公证，描述委托办理房产过户手续", "fields": ["张三", "110101199001011234", "委托公证", "房产过户"]}
                    ],
                    "expected": "申请提交成功，状态变为'待AI接待'",
                    "verify": "1.申请编号生成 2.流程状态正确更新 3.进入下一环节"
                },
                {
                    "id": "FLOW-02", "name": "申请信息不完整", "type": "负向",
                    "prerequisite": "申办人已登录",
                    "steps": "1.填写公证事项表 2.故意遗漏必填项 3.尝试提交",
                    "images": [],
                    "expected": "提示必填项未填写，阻止提交",
                    "verify": "1.未填写项高亮提示 2.提交按钮禁用"
                },
                {
                    "id": "FLOW-03", "name": "公证事项类型选择", "type": "正向",
                    "prerequisite": "申办人已登录",
                    "steps": "1.查看公证事项类型列表 2.选择合适的公证事项",
                    "images": [],
                    "expected": "成功选择公证事项，进入信息填写",
                    "verify": "1.事项类型列表完整 2.选择后进入对应表单"
                }
            ]
        },
        {
            "module": "2. AI接待（身份验证）",
            "test_cases": [
                {
                    "id": "FLOW-04", "name": "AI身份验证通过", "type": "正向",
                    "prerequisite": "申请已提交",
                    "steps": "1.AI自动接待 2.上传身份证照片 3.AI识别验证身份",
                    "images": [
                        {"func": create_id_card_positive, "name": "身份证正面", "prompt": "中华人民共和国居民身份证，姓名张三，性别男，民族汉族，1990年01月01日出生，住址北京市朝阳区建国路88号，身份证号110101199001011234", "fields": ["张三", "男", "汉族", "1990年01月01日", "110101199001011234"]}
                    ],
                    "expected": "身份验证通过，申办人信息自动回显",
                    "verify": "1.身份证信息识别准确 2.信息回显正确 3.进入公证员审查"
                },
                {
                    "id": "FLOW-05", "name": "AI身份验证失败-身份证模糊", "type": "负向",
                    "prerequisite": "进入AI接待",
                    "steps": "1.上传模糊的身份证照片 2.提交验证",
                    "images": [],
                    "expected": "提示'身份证照片不清晰，请重新拍摄'",
                    "verify": "1.能检测到模糊 2.提示清晰 3.允许重新上传"
                },
                {
                    "id": "FLOW-06", "name": "AI身份验证失败-非本人身份证", "type": "负向",
                    "prerequisite": "进入AI接待",
                    "steps": "1.上传他人身份证 2.提交验证",
                    "images": [],
                    "expected": "提示'身份证与申请人信息不一致'",
                    "verify": "1.能检测到不一致 2.阻止进入下一环节"
                },
                {
                    "id": "FLOW-07", "name": "身份验证超时", "type": "负向",
                    "prerequisite": "进入AI接待",
                    "steps": "1.长时间未上传身份证 2.等待超时",
                    "images": [],
                    "expected": "提示超时，引导重新发起或联系客服",
                    "verify": "1.超时机制生效 2.提示清晰"
                }
            ]
        },
        {
            "module": "3. 公证员审查",
            "test_cases": [
                {
                    "id": "FLOW-08", "name": "公证员审查通过", "type": "正向",
                    "prerequisite": "公证员账号登录",
                    "steps": "1.查看待审查申请列表 2.打开申请详情 3.审查材料完整性 4.点击'通过'",
                    "images": [],
                    "expected": "审查通过，流程进入出具公证书环节",
                    "verify": "1.申请信息展示完整 2.审批状态正确更新 3.申办人收到通知"
                },
                {
                    "id": "FLOW-09", "name": "公证员驳回申请-材料不全", "type": "负向",
                    "prerequisite": "公证员账号登录",
                    "steps": "1.审查申请材料 2.发现材料不完整 3.填写驳回原因 4.点击'驳回'",
                    "images": [],
                    "expected": "申请被驳回，申办人收到驳回通知及原因",
                    "verify": "1.驳回原因清晰 2.通知及时送达 3.申办人可重新发起"
                },
                {
                    "id": "FLOW-10", "name": "公证员驳回申请-不符合条件", "type": "负向",
                    "prerequisite": "公证员账号登录",
                    "steps": "1.审查申请 2.发现不符合公证条件 3.填写驳回原因 4.提交驳回",
                    "images": [],
                    "expected": "申请驳回，申办人收到通知",
                    "verify": "1.驳回原因准确 2.流程状态正确"
                },
                {
                    "id": "FLOW-11", "name": "驳回后重新发起", "type": "正向",
                    "prerequisite": "申请被驳回",
                    "steps": "1.查看驳回原因 2.补充/修改材料 3.重新提交申请",
                    "images": [],
                    "expected": "重新提交成功，进入新一轮审查流程",
                    "verify": "1.驳回原因可查看 2.重新提交成功 3.新流程正常启动"
                }
            ]
        },
        {
            "module": "4. 出具公证书",
            "test_cases": [
                {
                    "id": "FLOW-12", "name": "生成电子公证书", "type": "正向",
                    "prerequisite": "公证员审查通过",
                    "steps": "1.系统自动生成公证书 2.公证员在线签章 3.发放电子公证书",
                    "images": [
                        {"func": create_certificate, "name": "公证书", "prompt": "公证书，编号(2026)京公证字第1234号，申请人张三，委托事项房产过户，受托人李四，公证员李公证，北京市公证处，2026年04月08日", "fields": ["(2026)京公证字第1234号", "张三", "李四", "房产过户", "李公证", "2026年04月08日"]}
                    ],
                    "expected": "公证书生成成功，可查看和下载",
                    "verify": "1.公证书内容准确 2.签章显示正确 3.可正常下载PDF"
                },
                {
                    "id": "FLOW-13", "name": "公证书签章失败", "type": "负向",
                    "prerequisite": "公证书待签章",
                    "steps": "1.公证员进行签章操作 2.签章过程异常中断（网络断开）",
                    "images": [],
                    "expected": "签章失败，提示重新操作",
                    "verify": "1.异常提示清晰 2.可重新签章 3.不影响已生成内容"
                },
                {
                    "id": "FLOW-14", "name": "查看公证书详情", "type": "正向",
                    "prerequisite": "公证书已生成",
                    "steps": "1.进入公证书列表 2.点击查看详情 3.验证内容完整性",
                    "images": [],
                    "expected": "公证书详情页显示完整信息",
                    "verify": "1.所有字段显示正确 2.签章有效 3.可追溯"
                }
            ]
        },
        {
            "module": "5. 归档",
            "test_cases": [
                {
                    "id": "FLOW-15", "name": "正常归档", "type": "正向",
                    "prerequisite": "公证书已出具",
                    "steps": "1.系统自动归档 2.申办人查看归档状态",
                    "images": [],
                    "expected": "归档完成，状态显示'已归档'",
                    "verify": "1.归档状态正确 2.归档时间记录准确 3.可查询历史记录"
                },
                {
                    "id": "FLOW-16", "name": "归档异常处理", "type": "负向",
                    "prerequisite": "归档过程中",
                    "steps": "1.系统执行归档 2.发生异常错误",
                    "images": [],
                    "expected": "归档失败，提示重试",
                    "verify": "1.异常提示清晰 2.可手动重试 3.数据不丢失"
                }
            ]
        },
        {
            "module": "6. 流程状态与通知",
            "test_cases": [
                {
                    "id": "FLOW-17", "name": "全流程状态实时更新", "type": "正向",
                    "prerequisite": "申请进行中",
                    "steps": "1.查看申请详情页 2.查看流程进度 3.验证各环节状态",
                    "images": [],
                    "expected": "流程状态准确显示当前所处环节",
                    "verify": "1.状态与实际一致 2.进度条显示正确 3.时间节点准确"
                },
                {
                    "id": "FLOW-18", "name": "关键节点短信通知", "type": "正向",
                    "prerequisite": "申办人手机号已绑定",
                    "steps": "1.触发关键节点（受理、审批、出证、归档）2.检查短信接收",
                    "images": [],
                    "expected": "关键节点发送短信通知，用户收到",
                    "verify": "1.通知及时送达 2.内容准确 3.可退订"
                },
                {
                    "id": "FLOW-19", "name": "流程中断-网络异常", "type": "负向",
                    "prerequisite": "申请进行中",
                    "steps": "1.在提交环节断网 2.重新连接后查看状态",
                    "images": [],
                    "expected": "数据保护，提示重新提交或自动恢复",
                    "verify": "1.数据不丢失 2.恢复机制正常"
                },
                {
                    "id": "FLOW-20", "name": "流程取消-申办人主动取消", "type": "负向",
                    "prerequisite": "公证员审查前",
                    "steps": "1.申办人查看申请 2.点击'取消申请' 3.确认取消",
                    "images": [],
                    "expected": "申请取消，流程终止",
                    "verify": "1.取消成功 2.状态正确更新 3.通知公证员"
                }
            ]
        }
    ]

# ============================================================================
# 构建XMind数据
# ============================================================================

def build_xmind_data():
    test_data = get_test_data()
    branches = []

    # 根节点
    branches.append({
        "title": "存证转公证流程图 - 测试功能点",
        "children": [
            {
                "title": "1. 申办人发起申请",
                "children": [
                    {
                        "title": "FLOW-01：正常发起申请",
                        "children": [
                            "前置条件：申办人已登录",
                            "操作步骤：1.点击'发起申请' 2.填写公证事项表 3.提交申请",
                            "测试数据：公证事项申请表",
                            "预期结果：申请提交成功，状态变为'待AI接待'",
                            "验证点：1.申请编号生成 2.流程状态正确更新 3.进入下一环节"
                        ]
                    },
                    {
                        "title": "FLOW-02：申请信息不完整",
                        "children": [
                            "前置条件：申办人已登录",
                            "操作步骤：1.填写公证事项表 2.故意遗漏必填项 3.尝试提交",
                            "预期结果：提示必填项未填写，阻止提交"
                        ]
                    },
                    {
                        "title": "FLOW-03：公证事项类型选择",
                        "children": [
                            "前置条件：申办人已登录",
                            "操作步骤：1.查看公证事项类型列表 2.选择合适的公证事项",
                            "预期结果：成功选择公证事项，进入信息填写"
                        ]
                    }
                ]
            },
            {
                "title": "2. AI接待（身份验证）",
                "children": [
                    {
                        "title": "FLOW-04：AI身份验证通过",
                        "children": [
                            "前置条件：申请已提交",
                            "操作步骤：1.AI自动接待 2.上传身份证照片 3.AI识别验证身份",
                            "测试数据：身份证正面照片",
                            "预期结果：身份验证通过，申办人信息自动回显",
                            "验证点：1.身份证信息识别准确 2.信息回显正确 3.进入公证员审查"
                        ]
                    },
                    {
                        "title": "FLOW-05：AI身份验证失败-身份证模糊",
                        "children": [
                            "前置条件：进入AI接待",
                            "操作步骤：1.上传模糊的身份证照片 2.提交验证",
                            "预期结果：提示'身份证照片不清晰，请重新拍摄'"
                        ]
                    },
                    {
                        "title": "FLOW-06：AI身份验证失败-非本人身份证",
                        "children": [
                            "前置条件：进入AI接待",
                            "操作步骤：1.上传他人身份证 2.提交验证",
                            "预期结果：提示'身份证与申请人信息不一致'"
                        ]
                    },
                    {
                        "title": "FLOW-07：身份验证超时",
                        "children": [
                            "前置条件：进入AI接待",
                            "操作步骤：1.长时间未上传身份证 2.等待超时",
                            "预期结果：提示超时，引导重新发起或联系客服"
                        ]
                    }
                ]
            },
            {
                "title": "3. 公证员审查",
                "children": [
                    {
                        "title": "FLOW-08：公证员审查通过",
                        "children": [
                            "前置条件：公证员账号登录",
                            "操作步骤：1.查看待审查申请列表 2.打开申请详情 3.审查材料完整性 4.点击'通过'",
                            "预期结果：审查通过，流程进入出具公证书环节"
                        ]
                    },
                    {
                        "title": "FLOW-09：公证员驳回申请-材料不全",
                        "children": [
                            "前置条件：公证员账号登录",
                            "操作步骤：1.审查申请材料 2.发现材料不完整 3.填写驳回原因 4.点击'驳回'",
                            "预期结果：申请被驳回，申办人收到驳回通知及原因"
                        ]
                    },
                    {
                        "title": "FLOW-10：公证员驳回申请-不符合条件",
                        "children": [
                            "前置条件：公证员账号登录",
                            "操作步骤：1.审查申请 2.发现不符合公证条件 3.填写驳回原因 4.提交驳回",
                            "预期结果：申请驳回，申办人收到通知"
                        ]
                    },
                    {
                        "title": "FLOW-11：驳回后重新发起",
                        "children": [
                            "前置条件：申请被驳回",
                            "操作步骤：1.查看驳回原因 2.补充/修改材料 3.重新提交申请",
                            "预期结果：重新提交成功，进入新一轮审查流程"
                        ]
                    }
                ]
            },
            {
                "title": "4. 出具公证书",
                "children": [
                    {
                        "title": "FLOW-12：生成电子公证书",
                        "children": [
                            "前置条件：公证员审查通过",
                            "操作步骤：1.系统自动生成公证书 2.公证员在线签章 3.发放电子公证书",
                            "测试数据：公证书",
                            "预期结果：公证书生成成功，可查看和下载"
                        ]
                    },
                    {
                        "title": "FLOW-13：公证书签章失败",
                        "children": [
                            "前置条件：公证书待签章",
                            "操作步骤：1.公证员进行签章操作 2.签章过程异常中断（网络断开）",
                            "预期结果：签章失败，提示重新操作"
                        ]
                    },
                    {
                        "title": "FLOW-14：查看公证书详情",
                        "children": [
                            "前置条件：公证书已生成",
                            "操作步骤：1.进入公证书列表 2.点击查看详情 3.验证内容完整性",
                            "预期结果：公证书详情页显示完整信息"
                        ]
                    }
                ]
            },
            {
                "title": "5. 归档",
                "children": [
                    {
                        "title": "FLOW-15：正常归档",
                        "children": [
                            "前置条件：公证书已出具",
                            "操作步骤：1.系统自动归档 2.申办人查看归档状态",
                            "预期结果：归档完成，状态显示'已归档'"
                        ]
                    },
                    {
                        "title": "FLOW-16：归档异常处理",
                        "children": [
                            "前置条件：归档过程中",
                            "操作步骤：1.系统执行归档 2.发生异常错误",
                            "预期结果：归档失败，提示重试"
                        ]
                    }
                ]
            },
            {
                "title": "6. 流程状态与通知",
                "children": [
                    {
                        "title": "FLOW-17：全流程状态实时更新",
                        "children": [
                            "前置条件：申请进行中",
                            "操作步骤：1.查看申请详情页 2.查看流程进度 3.验证各环节状态",
                            "预期结果：流程状态准确显示当前所处环节"
                        ]
                    },
                    {
                        "title": "FLOW-18：关键节点短信通知",
                        "children": [
                            "前置条件：申办人手机号已绑定",
                            "操作步骤：1.触发关键节点（受理、审批、出证、归档）2.检查短信接收",
                            "预期结果：关键节点发送短信通知，用户收到"
                        ]
                    },
                    {
                        "title": "FLOW-19：流程中断-网络异常",
                        "children": [
                            "前置条件：申请进行中",
                            "操作步骤：1.在提交环节断网 2.重新连接后查看状态",
                            "预期结果：数据保护，提示重新提交或自动恢复"
                        ]
                    },
                    {
                        "title": "FLOW-20：流程取消-申办人主动取消",
                        "children": [
                            "前置条件：公证员审查前",
                            "操作步骤：1.申办人查看申请 2.点击'取消申请' 3.确认取消",
                            "预期结果：申请取消，流程终止"
                        ]
                    }
                ]
            }
        ]
    })

    return {
        "root_title": "存证转公证流程图 - 测试功能点",
        "sheet_title": "测试用例",
        "branches": branches
    }

# ============================================================================
# 生成HTML
# ============================================================================

def generate_html():
    test_data = get_test_data()

    # 生成所有图片
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

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>存证转公证流程图 - 测试功能点</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei", Arial, sans-serif; background: #1a1a2e; color: #eee; min-height: 100vh; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; }
.header h1 { font-size: 28px; margin-bottom: 10px; }
.header p { opacity: 0.9; font-size: 14px; }
.container { max-width: 1400px; margin: 0 auto; padding: 20px; }
.summary { background: #16213e; border-radius: 12px; padding: 25px; margin-bottom: 30px; }
.summary h2 { color: #667eea; margin-bottom: 15px; }
.stats { display: flex; gap: 30px; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-number { font-size: 36px; font-weight: bold; color: #667eea; }
.stat-label { color: #9ca3af; font-size: 13px; }
.module { background: #16213e; border-radius: 12px; margin-bottom: 30px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.module-header { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.module-header h2 { font-size: 20px; }
.module-header .toggle { font-size: 24px; transition: transform 0.3s; }
.module-content { padding: 20px; display: none; }
.module-content.show { display: block; }
.test-case { background: #1f2937; border-radius: 10px; margin-bottom: 20px; overflow: hidden; border-left: 4px solid #667eea; }
.test-case.negative { border-left-color: #ef4444; }
.test-case-header { background: #374151; padding: 15px 20px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.test-case-header:hover { background: #4b5563; }
.test-case-header h3 { font-size: 16px; color: #fff; }
.type-tag { padding: 4px 12px; border-radius: 20px; font-size: 12px; }
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
.prompt-label { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.prompt-label span { color: #60a5fa; font-weight: bold; font-size: 13px; }
.copy-btn { background: #60a5fa; color: #1a1a2e; border: none; padding: 4px 12px; border-radius: 15px; font-size: 11px; cursor: pointer; font-weight: bold; }
.copy-btn:hover { background: #93c5fd; }
.prompt { display: none; }
.prompt-text { font-family: monospace; white-space: pre-wrap; word-break: break-all; color: #93c5fd; background: #1a1a2e; padding: 12px; border-radius: 8px; font-size: 13px; line-height: 1.6; border-left: 3px solid #60a5fa; }
.field-row { margin-top: 10px; }
.field-row span { color: #9ca3af; font-size: 12px; }
.field-tag { background: #4b5563; padding: 4px 10px; border-radius: 15px; font-size: 12px; color: #d1d5db; margin-right: 5px; }
.lightbox { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); display: none; justify-content: center; align-items: center; z-index: 1000; cursor: zoom-out; }
.lightbox.show { display: flex; }
.lightbox img { max-width: 90%; max-height: 90%; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
.lightbox-info { position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); padding: 15px 30px; border-radius: 30px; color: white; }
</style>
</head>
<body>
<div class="header">
    <h1>存证转公证流程图 - 测试功能点</h1>
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
                    fields_html = "".join([f'<span class="field-tag">{f}</span>' for f in img_info["fields"]]) if img_info["fields"] else '<span class="field-tag" style="background:#ef4444">无关键字段</span>'
                    prompt_text = img_info["prompt"]
                    html += f'''
                        <div class="image-card">
                            <img src="data:image/png;base64,{img_data.get("base64", "")}" onclick="openLightbox(this)" alt="{img_info["name"]}">
                            <div class="image-info">
                                <h4>{img_info["name"]}</h4>
                                <div class="prompt-label">
                                    <span>📋 AI增强提示词</span>
                                    <button class="copy-btn" onclick="copyPrompt(this)">复制</button>
                                </div>
                                <div class="prompt">{prompt_text}</div>
                                <div class="prompt-text">{prompt_text}</div>
                                <div class="field-row">
                                    <span>关键字段：</span>
                                    {fields_html}
                                </div>
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

    html += '''
    <div class="lightbox" onclick="closeLightbox()">
        <img src="" alt="">
        <div class="lightbox-info"></div>
    </div>
</div>
<script>
function toggleModule(header) {
    const content = header.nextElementSibling;
    const toggle = header.querySelector(".toggle");
    content.classList.toggle("show");
    toggle.style.transform = content.classList.contains("show") ? "rotate(180deg)" : "";
}
function toggleTestCase(header) {
    const content = header.nextElementSibling;
    content.classList.toggle("show");
}
function openLightbox(img) {
    event.stopPropagation();
    const lightbox = document.querySelector(".lightbox");
    const lightboxImg = lightbox.querySelector("img");
    const lightboxInfo = lightbox.querySelector(".lightbox-info");
    lightboxImg.src = img.src;
    lightboxInfo.textContent = img.alt;
    lightbox.classList.add("show");
}
function closeLightbox() {
    document.querySelector(".lightbox").classList.remove("show");
}
function copyPrompt(btn) {
    const card = btn.closest(".image-card");
    const promptEl = card.querySelector(".prompt");
    const text = promptEl.textContent;
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = "已复制!";
        btn.style.background = "#10b981";
        setTimeout(() => {
            btn.textContent = "复制";
            btn.style.background = "#60a5fa";
        }, 1500);
    });
}
document.querySelector(".module-header").click();
</script>
</body>
</html>'''

    return html

# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 60)
    print("存证转公证流程图 - 测试功能点生成")
    print("=" * 60)

    # Step 1: 生成XMind
    print("\n[Step 1] 生成XMind文件...")
    xmind_data = build_xmind_data()
    xmind_path = os.path.join(OUTPUT_ROOT, "存证转公证流程图.xmind")
    create_xmind(xmind_data, xmind_path)
    print(f"[OK] XMind: {xmind_path}")

    # Step 2: 生成HTML
    print("\n[Step 2] 生成HTML文件（含图片）...")
    html = generate_html()
    html_path = os.path.join(OUTPUT_ROOT, "存证转公证流程图_含图片.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] HTML: {html_path}")

    # Step 3: 生成图片文件夹
    print("\n[Step 3] 生成测试图片文件夹...")
    test_data = get_test_data()
    module_dir = os.path.join(OUTPUT_ROOT, "test_data")
    os.makedirs(module_dir, exist_ok=True)

    for module_data in test_data:
        for tc in module_data["test_cases"]:
            for img_info in tc.get("images", []):
                img = img_info["func"]()
                img_path = os.path.join(module_dir, f"{tc['id']}_{img_info['name']}.png")
                img.save(img_path)

                # 提示词文件
                prompt_path = img_path.replace(".png", "_提示词.md")
                with open(prompt_path, "w", encoding="utf-8") as f:
                    f.write(f"# {img_info['name']}\n\n")
                    f.write(f"**测试用例**: {tc['id']} - {tc['name']}\n\n")
                    f.write(f"**类型**: {tc['type']}\n\n")
                    f.write(f"## AI增强提示词\n\n{img_info['prompt']}\n\n")
                    if img_info.get("fields"):
                        f.write(f"## 关键字段\n\n")
                        for field in img_info["fields"]:
                            f.write(f"- {field}\n")

    print(f"[OK] 图片文件夹: {OUTPUT_ROOT}/test_data/")

    print("\n" + "=" * 60)
    print("生成完成！")
    print("=" * 60)
    print(f"\n输出目录：{OUTPUT_ROOT}")
    print(f"\n生成文件：")
    print(f"  1. XMind文件：存证转公证流程图.xmind")
    print(f"  2. HTML文件：存证转公证流程图_含图片.html")
    print(f"  3. 测试图片：test_data/*.png")

if __name__ == "__main__":
    main()
