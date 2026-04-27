# -*- coding: utf-8 -*-
"""
Axure原型测试用例生成技能

功能：
1. 访问Axure原型页面，分析多轮对话流程
2. 生成测试用例截图
3. 使用多模态AI生成逼真的测试数据图片
4. 整理文件夹结构
5. 为文本类AI功能生成.md文档（AI润色、AI扩写、AI缩写、AI隐私等）

支持的模块类型：
- 出行类：火车票、机票、打车发票、驾驶证、步行记录等
- 婚育类：结婚证、离婚证、出生证明、产检报告等
- 身后类：遗嘱公证、死亡证明、火化证明等
- 养老类：养老保险、养老金发放、社会保障卡等
- 时间轴类：文本记录、AI润色、AI扩写、AI缩写、AI隐私等

用法：
    python extract_prototype.py --url "https://xxx.com/原型.html" --module "出行"
    python extract_prototype.py --url "https://xxx.com/原型.html" --module "时间轴"
    python extract_prototype.py --url "https://xxx.com/原型.html" --module "婚育" --ai-generate
"""

import os
import sys
import io
import json
import base64
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


class MultimodalImageGenerator:
    """多模态AI图像生成器

    使用多模态AI模型生成逼真的测试数据图片。

    支持的API：
    - Claude API (Anthropic)
    - OpenAI GPT-4V / DALL-E 3
    - 通义千问 VL
    - 智谱 GLM-4V

    使用示例：
        generator = MultimodalImageGenerator(api_type="claude")
        generator.generate_document_image(
            prompt="生成一张中国火车票，蓝色背景，白色文字，车次G1234",
            output_path="train_ticket.png"
        )
    """

    def __init__(self, api_type: str = "claude", api_key: str = None):
        """初始化生成器

        Args:
            api_type: API类型，可选值：claude, openai, qwen, zhipu
            api_key: API密钥，如不提供则从环境变量读取
        """
        self.api_type = api_type.lower()
        self.api_key = api_key or self._get_api_key()

    def _get_api_key(self) -> str:
        """从环境变量获取API密钥"""
        env_vars = {
            'claude': ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],
            'openai': ['OPENAI_API_KEY'],
            'qwen': ['DASHSCOPE_API_KEY', 'QWEN_API_KEY'],
            'zhipu': ['ZHIPU_API_KEY', 'GLM_API_KEY'],
        }
        for var in env_vars.get(self.api_type, []):
            if os.getenv(var):
                return os.getenv(var)
        return None

    def _call_claude_api(self, prompt: str, image_size: str = "1024x1024",
                        reference_image: Image = None) -> bytes:
        """调用Claude API生成图像

        注意：需要安装 anthropic 包
        pip install anthropic

        如果设置了 MINIMAX_API_KEY，优先使用MiniMax REST API
        """
        # 检查是否使用MiniMax API
        # 条件：设置了MINIMAX_API_KEY环境变量，或ANTHROPIC_BASE_URL包含minimax，或API密钥是MiniMax格式(sk-cp-)
        api_key = self.api_key or os.environ.get('MINIMAX_API_KEY', '')
        use_minimax = (
            os.environ.get('MINIMAX_API_KEY') or
            'minimax' in os.environ.get('ANTHROPIC_BASE_URL', '').lower() or
            api_key.startswith('sk-cp-')
        )
        if use_minimax:
            return self._call_minimax_image_api(prompt, reference_image=reference_image)

        try:
            import anthropic
            base_url = os.environ.get('ANTHROPIC_BASE_URL')
            if base_url:
                client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=base_url
                )
            else:
                client = anthropic.Anthropic(api_key=self.api_key)

            # 尝试使用官方Claude API格式
            response = client.beta.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""{prompt}

请生成图片。"""
                            }
                        ]
                    }
                ],
                tools=[{"type": "image_generation"}],
                tool_choice={"type": "tool", "name": "image_generation"}
            )

            for content in response.content:
                if content.type == "image":
                    return base64.b64decode(content.source.data)

        except Exception as e:
            print(f"Claude API调用失败: {e}")

            # 尝试MiniMax兼容格式
            try:
                return self._call_minimax_image_api(prompt)
            except:
                pass

        return None

    def _call_minimax_image_api(self, prompt: str, reference_image: Image = None) -> bytes:
        """调用MiniMax图像生成API

        MiniMax API格式，支持img2img（传入参考图）。
        """
        try:
            import requests

            # MiniMax图像生成API
            url = "https://api.minimaxi.com/v1/image_generation"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "image-01",
                "prompt": prompt,
                "n": 1,
                "response_format": "base64"
            }

            # 如果提供了参考图，使用img2img模式
            if reference_image is not None:
                buf = io.BytesIO()
                # 确保转为RGB
                ref_img = reference_image.convert('RGB')
                ref_img.save(buf, format='PNG')
                b64_img = base64.b64encode(buf.getvalue()).decode()
                data['image_base64'] = b64_img

            response = requests.post(url, headers=headers, json=data, timeout=120)

            if response.status_code == 200:
                try:
                    result = response.json()
                except Exception:
                    result = None
                if result is None:
                    print(f"MiniMax API响应无法解析JSON: status={response.status_code}, body={response.text[:300]}")
                    return None
                # MiniMax返回格式: {"data": {"image_base64": "..."}}（response_format=base64）
                # 备选旧格式: {"data": {"image_urls": [...]}}（默认或response_format=url）
                image_data = (result or {}).get('data') or {}
                image_base64 = image_data.get('image_base64') or []
                image_urls = image_data.get('image_urls') or []

                if image_base64 and len(image_base64) > 0:
                    # base64格式：直接解码
                    import base64 as b64_module
                    img_bytes = b64_module.b64decode(image_base64[0])
                    print(f"MiniMax图像生成成功（base64）")
                    return img_bytes
                elif image_urls and len(image_urls) > 0:
                    # URL格式：下载图像
                    image_url = image_urls[0]
                    img_response = requests.get(image_url, timeout=60)
                    if img_response.status_code == 200:
                        print(f"MiniMax图像生成成功（URL）")
                        return img_response.content
                else:
                    print(f"MiniMax API返回格式异常: {str(result)[:200]}")
            else:
                print(f"MiniMax API错误: {response.status_code} - {response.text[:300]}")

        except Exception as e:
            print(f"MiniMax API调用失败: {e}")

        return None

    def _call_openai_api(self, prompt: str, size: str = "1024x1024") -> bytes:
        """调用OpenAI API生成图像（使用DALL-E 3）"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.images.generate(
                model="dall-e-3",
                prompt=f"""生成一张用于AI识别测试的真实感图片。

要求：
1. 图片内容必须清晰、真实、便于OCR识别
2. 文字必须是真实可读的中文或英文
3. 证件类图片需要有真实的证件版式、照片框和印章
4. 票据类图片需要有真实的票据格式和条形码

{prompt}

请生成最真实的效果。""",
                size="1024x1024",
                quality="standard",
                n=1
            )

            image_url = response.data[0].url
            # 下载图像
            import requests
            response = requests.get(image_url)
            return response.content

        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return None

    def _call_qwen_api(self, prompt: str) -> bytes:
        """调用通义千问VL API生成图像"""
        try:
            import dashscope
            from dashscope import MultiModalConversation

            dashscope.api_key = self.api_key

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": f"""请生成一张用于OCR识别测试的真实感图片。

图片要求：
1. 清晰、真实、中文可读
2. 证件类需要有真实版式和印章
3. 票据类需要有真实格式

{prompt}

生成图片并输出。"""}
                    ]
                }
            ]

            response = MultiModalConversation.call(
                model="qwen-vl-plus",
                messages=messages
            )

            if response.output and response.output.choices:
                image_data = response.output.choices[0].message.content[0].get("image")
                if image_data:
                    return base64.b64decode(image_data)

        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return None

    def generate_image(self, prompt: str, output_path: str = None,
                      fallback_image: Image = None,
                      reference_image: Image = None) -> Image:
        """使用多模态AI生成图像（img2img方案）

        Args:
            prompt: 图像描述提示词
            output_path: 输出路径
            fallback_image: 如果API调用失败，使用的备用图像
            reference_image: PIL参考图像（文档），作为img2img的参考图传给AI，
                            AI会理解文档结构并生成同结构但更真实的结果，同时保留文字

        Returns:
            PIL Image对象
        """
        image_data = None

        # 根据API类型调用对应的API
        if self.api_type == "claude":
            image_data = self._call_claude_api(prompt, reference_image=reference_image)
        elif self.api_type == "openai":
            image_data = self._call_openai_api(prompt)
        elif self.api_type == "qwen":
            image_data = self._call_qwen_api(prompt)

        # 如果API调用成功，加载图像并保存
        if image_data:
            img = Image.open(io.BytesIO(image_data))
            if output_path:
                img.save(output_path)
                print(f"Generated: {output_path}")
            return img

        # API调用失败，使用备用图像
        if fallback_image:
            if output_path:
                fallback_image.save(output_path)
                print(f"Generated (fallback): {output_path}")
            return fallback_image

        print(f"Warning: Failed to generate image for prompt: {prompt[:50]}...")
        return None

    def _blend_ai_texture(self, ai_img: Image, pil_doc: Image) -> Image:
        """将AI纹理叠加到PIL完整文档上（Multiply混合）

        策略：PIL完整文档做底层（文字和结构正确），AI纹理做上层（质感增强）
        - 使用Multiply混合模式：白色区域透出AI纹理，彩色区域叠加色调
        - 文字和关键结构保持清晰，背景获得AI生成的质感

        Args:
            ai_img: AI生成的纹理/背景图片
            pil_doc: PIL完整文档（RGB，包含所有文字和结构）

        Returns:
            合成后的图片
        """
        import numpy as np

        target_w, target_h = pil_doc.size

        # 调整AI图片尺寸以匹配PIL文档
        if ai_img.size != (target_w, target_h):
            ai_resized = ai_img.resize((target_w, target_h), Image.LANCZOS)
        else:
            ai_resized = ai_img.copy()

        # 转换为RGB模式
        if ai_resized.mode != 'RGB':
            ai_resized = ai_resized.convert('RGB')
        if pil_doc.mode != 'RGB':
            pil_doc = pil_doc.convert('RGB')

        # Multiply混合：将两层逐像素相乘再除以255
        # result = (pil_pixel * ai_pixel) / 255
        # 白色(255) * AI = AI（不变）；深色 * AI = 加深
        pil_arr = np.array(pil_doc, dtype=np.float32)
        ai_arr = np.array(ai_resized, dtype=np.float32)

        # Multiply混合
        result_arr = (pil_arr * ai_arr) / 255.0
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)

        return Image.fromarray(result_arr)


class PrototypeTestCaseGenerator:
    """Axure原型测试用例生成器

    用法示例：
        generator = PrototypeTestCaseGenerator(
            url="https://xxx.com/原型.html",
            module_name="出行",
            output_dir="C:/testcases"
        )

        # 使用AI生成逼真的测试图片
        generator.generate_all_test_data(use_ai=True)

        # 生成特定模块的测试数据
        generator.generate_travel_test_data(use_ai=True)
        generator.generate_timeline_test_data(use_ai=True)
    """

    # 通用颜色主题
    COLORS = {
        'blue': '#1a5fb4',
        'green': '#26a269',
        'purple': '#9141ac',
        'red': '#c01c28',
        'cyan': '#1c71d8',
        'yellow': '#e5a50a',
    }

    # AI图像生成提示词模板
    AI_IMAGE_PROMPTS = {
        'train_ticket': """生成一张中国高铁火车票的真实照片。
要求：
- 蓝色渐变背景，白色文字
- 车次：G1234（红色醒目显示）
- 出发站：北京南
- 到达站：上海虹桥
- 日期：{date}，出发时间：08:30，到达时间：12:45
- 票价：553.00元
- 座位：二等座 08车 12A号
- 乘客姓名：张三
- 底部有磁条区域和条形码
- 整体风格真实，有票面质感

请生成最真实的火车票效果。""",

        'flight_ticket': """生成一张中国民航电子客票行程单的真实照片。
要求：
- 白色背景，绿色主色调
- 航班号：MU5137（中国东方航空）
- 出发：PEK 北京首都机场 T3
- 到达：SHA 上海虹桥机场 T2
- 日期：{date}，出发时间：14:30，到达时间：16:45
- 乘客：李四
- 舱位：经济舱，座位：23K
- 票价：880.00元（含税）
- 右上角有航空公司logo
- 底部有条形码

请生成真实的机票效果。""",

        'taxi_invoice': """生成一张北京出租车发票的真实照片。
要求：
- 白色小票纸样式
- 发票代码：111001600111
- 发票号码：12345678
- 出租车号：京BQ8888
- 上下车时间：2026-03-30 09:15 - 09:45
- 单价：3.00元/公里
- 里程：12.5公里
- 等候时间：5分钟
- 金额：48.00元
- 发票专用章
- 底部有二维码

请生成真实的出租车发票效果。""",

        'driving_license': """生成一张中国机动车驾驶证的正面照片。
要求：
- 暗红色塑料外壳质感
- 证芯为浅绿色背景
- 准驾车型：C1
- 姓名：张三
- 性别：男
- 国籍：中国
- 出生日期：1990-01-01
- 地址：北京市朝阳区
- 证号：110105199001011234
- 有效期限：2020-01-01至2026-01-01
- 右上角有证件照片位置（可放照片）
- 红色印章

请生成真实的驾驶证效果。""",

        'will_notary': """生成一张中国遗嘱公证书的真实照片。
要求：
- 白色背景，蓝色标题栏
- 标题：遗嘱公证书
- 立遗嘱人：张三
- 身份证：110105199001011234
- 公证编号：YZ202603300001
- 遗嘱内容：房产由子女继承
- 立遗嘱日期：2020年06月01日
- 公证日期：2020年06月15日
- 公证员：李公证
- 公证处：北京市公证处
- 状态：有效（绿色醒目显示）
- 底部有红色公证专用章
- 左侧有公证处标志图案

请生成真实的遗嘱公证书效果。""",

        'marriage_certificate': """生成一张中华人民共和国结婚证的封面和内页照片。
要求：
- 红色硬皮封面，上面有"结婚证"三个金色大字
- 国徽图案在封面中央
- 内页：
  - 左边：夫妻合影照片框
  - 右边：夫：张三，妻：李四
  - 夫身份证：110105199001011234
  - 妻身份证：110105199501015678
  - 登记日期：2020年05月20日
  - 登记机关：北京市民政局
  - 结婚证号：J202005200001
- 底部有红色民政局印章

请生成真实的结婚证效果。""",

        'divorce_certificate': """生成一张中华人民共和国离婚证的封面和内页照片。
要求：
- 深蓝色硬皮封面，上面有"离婚证"三个金色大字
- 内页：
  - 姓名：张三
  - 离婚证号：L20260301001
  - 身份证：110105199001011234
  - 登记日期：2020年05月20日
  - 离婚日期：2026年03月01日
  - 登记机关：北京市民政局
  - 离婚方式：协议离婚
- 底部有蓝色民政局印章

请生成真实的离婚证效果。""",

        'birth_certificate': """生成一张出生医学证明的照片。
要求：
- 浅蓝色背景
- 标题：出生医学证明
- 新生儿姓名：张小一
- 性别：男
- 出生体重：3500克
- 出生日期：2026年01月15日 10:30
- 出生医院：北京市妇幼保健院
- 母亲姓名：李四，身份证：110105199501015678
- 父亲姓名：张三，身份证：110105199001011234
- 右上角有条形码
- 底部有医院印章

请生成真实的出生证明效果。""",

        'death_certificate': """生成一张死亡医学证明书的照片。
要求：
- 白色背景，红色标题
- 标题：死亡医学证明书
- 死者姓名：张三
- 性别：男
- 年龄：36岁
- 身份证：110105199001011234
- 死亡日期：2026年03月25日
- 死亡地点：北京市人民医院
- 死亡原因：疾病
- 出具机构：北京市人民医院
- 医师签字：XXX
- 底部有医院红色印章

请生成真实的死亡证明效果。""",

        'pension_record': """生成一张中国社会保险缴费记录单的照片。
要求：
- 白色背景，蓝色标题条
- 标题：社会保险缴费记录
- 姓名：李四
- 社保账号：110105199501015678
- 缴费类型：养老保险（重点显示）
- 缴费期间：2020年01月至2026年03月
- 发放时间：2026-03-15
- 缴费月数：74个月
- 个人缴费：2500元/月
- 单位缴费：5000元/月
- 缴费基数：12500元
- 累计本金：555000元（绿色醒目）
- 底部有社保局印章

请生成真实的社会保险记录效果。""",

        'text_record': """生成一张时间轴记录的截图照片。
要求：
- 手机屏幕截图样式
- 顶部蓝色标题栏：时间轴记录
- 内容：
  - 标题：2026年春节
  - 日期：2026-01-28
  - 地点：北京
  - 内容：春节期间在北京与家人团聚，游览了故宫和长城。
  - 标签：旅行,家庭（绿色标签样式）
- 背景为白色
- 底部有操作按钮

请生成真实的手机应用截图效果。""",

        'ai_polish': """生成一张AI润色功能的效果截图。
要求：
- 手机屏幕截图样式
- 顶部绿色标题栏：AI润色
- 对比展示：
  - 上部分为浅灰色背景框，标注"原始文本"
  - 内容：今天去北京玩很开心。故宫很大，长城很长。
  - 下部分为白色背景框，标注"润色后"（绿色）
  - 内容：大年初一，我与家人一同前往北京，游览了气势恢宏的故宫与绵延起伏的长城，度过了愉快而难忘的春节假期。
- 润色类型选择栏：正式书面、文艺清新、幽默风趣

请生成真实的AI应用截图效果。""",

        'no_info': """生成一张普通风景照片（用于测试无相关信息的情况）。
要求：
- 一张美丽的自然风景照片
- 蓝天白云、青山绿水
- 或者城市街景
- 画面中不包含任何证件、票据、文件等
- 真实摄影风格，不是文档扫描件

请生成真实的风景照片。""",

        # ========== AI背景提示词（无文字，用于分层合成）==========
        # 这些提示词只描述视觉元素，不含任何文字
        # 生成后用PIL渲染正确的中文叠加在上层

        'train_ticket_bg': """Generate a photorealistic Chinese high-speed train ticket.
Requirements:
- Blue gradient background, white text areas
- Train number area in red (G/D/C series)
- Departure and arrival stations layout
- Date and time fields visible
- Price field visible
- Seat class and car/seat layout
- Passenger photo placeholder area
- Magnetic strip area at bottom
- Barcode area at bottom
- Real ticket paper texture, slight wear edges
- Overall style: authentic ticket, photographic quality, not flat design

Generate the most realistic train ticket visual. No Chinese text needed in the image - leave text areas blank or with placeholder lines.""",

        'flight_ticket_bg': """Generate a photorealistic Chinese airline e-ticket/itinerary receipt.
Requirements:
- White background, green main color tones
- Airline logo area (top right)
- Flight number and airline fields layout
- Departure and arrival airports with terminal info
- Date and time layout
- Passenger name field visible
- Cabin class and seat layout
- Ticket price area
- Barcode at bottom
- Official airline document style, printed receipt texture
- Realistic thermal printer paper quality

Generate authentic airline ticket visual. Leave text areas blank or with placeholder lines.""",

        'taxi_invoice_bg': """Generate a photorealistic Beijing taxi receipt/invoice.
Requirements:
- White thermal paper receipt style
- Invoice code and number fields
- Taxi license plate number field
- Pickup and dropoff timestamp fields
- Distance and waiting time fields
- Fare breakdown layout
- Total amount field in larger font
- Official stamp/seal area
- QR code at bottom
- Thermal paper texture with slight aging
- Real receipt print quality

Generate authentic taxi receipt visual. Leave text areas blank.""",

        'health_report_bg': """Generate a photorealistic Chinese health examination report.
Requirements:
- White A4 paper document style
- Hospital logo and header area
- Document title area at top
- Table rows for examination items
- Date and hospital name fields
- Doctor signature and seal area
- Hospital official stamp (red circle with Chinese characters)
- Professional medical document layout
- Clean document scan quality

Generate authentic health report visual. Leave text areas blank or with faint placeholder lines.""",

        'job_registration_bg': """Generate a photorealistic Chinese job registration form.
Requirements:
- White official form paper style
- Form title area at top
- Name and contact fields layout
- Job intention fields
- Work experience section
- Education background section
- Expected salary field
- Official seal area
- Form number and date fields
- Professional government form style
- Slight paper texture

Generate authentic job registration form visual. Leave text areas blank.""",

        'map_screenshot_bg': """Generate a photorealistic smartphone navigation map screenshot.
Requirements:
- Smartphone screen proportions
- Map application interface style (similar to Amap/Baidu Maps)
- Route line displayed on map
- Starting point and destination markers
- Distance and ETA fields layout
- Navigation instruction panel at bottom
- Map tiles visible (streets, buildings)
- Realistic smartphone screenshot quality
- iOS or Android map app style

Generate authentic navigation screenshot visual. Leave text areas blank.""",

        'travel_record_bg': """Generate a photorealistic smartphone travel record summary screenshot.
Requirements:
- Smartphone screen proportions
- Travel/commute record list interface
- Multiple record entries layout
- Date and amount fields for each entry
- Summary total area
- Transportation type icons (subway, taxi, train, plane)
- Mobile app list view style
- iOS or Android mobile banking/travel app style

Generate authentic travel record screenshot visual. Leave text areas blank.""",

        'app_screenshot_bg': """Generate a photorealistic smartphone app interface screenshot.
Requirements:
- iPhone or Android smartphone screen proportions
- Clean mobile app interface style
- List or card-based layout
- Status bar at top
- Bottom navigation or action button area
- Professional mobile app design
- Light background with subtle shadows
- Modern UI style

Generate authentic app screenshot visual. Leave text areas blank.""",

        'warning_message_bg': """Generate a photorealistic warning message dialog screenshot.
Requirements:
- Alert dialog box style (white background with red/orange border)
- Warning icon area at top (exclamation mark in triangle)
- Clear message text layout
- Single action button visible
- System dialog aesthetic
- Real mobile app or web interface style

Generate authentic warning dialog. Leave text blank.""",

        'network_error_bg': """Generate a photorealistic network error screen.
Requirements:
- Error page style (gray/light background)
- Broken connection icon or cloud-off icon visible
- Error message area visible
- Retry button visible
- Clean error page aesthetic
- Real mobile browser or app error state style

Generate authentic network error screen. Leave text areas blank.""",

        'cancel_dialog_bg': """Generate a photorealistic cancel confirmation dialog.
Requirements:
- Confirmation dialog box (white background)
- Question or info icon visible
- Two buttons: confirm/cancel
- Neutral/gray color scheme
- Clean modal dialog aesthetic
- Real mobile app or web confirmation style

Generate authentic dialog. Leave text areas blank.""",

        'multiple_records_bg': """Generate a photorealistic list view of multiple records.
Requirements:
- White background, clean list layout
- Multiple list items with icons and amounts
- Each row has: icon (left), description (middle), amount (right)
- Transportation type icons (bus, car, train, plane symbols)
- Total summary area at bottom
- Mobile banking or expense tracker app style

Generate authentic list view. Leave text areas blank.""",

        'supplementary_bg': """Generate a photorealistic smartphone app form screen.
Requirements:
- White form background
- Already filled information displayed at top
- Form fields with labels and input areas
- Additional info input section visible
- Submit/autofill button at bottom
- Clean professional app form aesthetic

Generate authentic form screen. Leave text areas blank.""",

        'no_info_bg': """Generate a photorealistic scenic landscape photograph.
Requirements:
- Beautiful natural landscape photo
- Blue sky with white clouds, green mountains, rivers
- Or city street scene
- No documents, tickets, certificates, receipts in the frame
- Real photographic style, not document scan
- High quality digital camera photo
- Natural scenery, mountains, lakes, trees

Generate authentic beautiful scenic photograph. No text, no documents.""",

        'cancel_operation_bg': """Generate a photorealistic cancel confirmation dialog.
Requirements:
- Confirmation dialog box (white background)
- Question or info icon visible
- Two buttons: confirm/cancel
- Neutral/gray color scheme
- Clean modal dialog aesthetic
- Real mobile app or web confirmation style

Generate authentic dialog. Leave text areas blank.""",
    }

    def __init__(self, url: str, module_name: str = None, output_dir: str = None,
                 use_ai: bool = False, ai_api_type: str = "claude"):
        """初始化生成器

        Args:
            url: Axure原型页面URL
            module_name: 模块名称，不提供则自动从URL提取
            output_dir: 输出目录，默认在当前目录创建 {module_name}testcases
            use_ai: 是否使用AI生成逼真图片，默认False使用PIL生成简单图片
            ai_api_type: AI API类型，可选：claude, openai, qwen, zhipu
        """
        self.url = url
        self.module_name = module_name or self._extract_module_name(url)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / f"{self.module_name}testcases"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # AI生成模式
        self.use_ai = use_ai
        self.ai_api_type = ai_api_type

        # 获取API密钥
        self._ai_api_key = self._get_ai_api_key()

        # 字体设置
        self._setup_fonts()

        # 创建目录结构
        self._create_directories()

    def _setup_fonts(self):
        """设置字体"""
        try:
            self.font_path = "C:/Windows/Fonts/msyh.ttc"
            self.title_font = ImageFont.truetype(self.font_path, 40)
            self.text_font = ImageFont.truetype(self.font_path, 28)
            self.small_font = ImageFont.truetype(self.font_path, 20)
        except:
            self.title_font = ImageFont.load_default()
            self.text_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    def _create_directories(self):
        """创建目录结构"""
        (self.output_dir / 'positive').mkdir(exist_ok=True)
        (self.output_dir / 'negative').mkdir(exist_ok=True)
        (self.output_dir / 'test_data').mkdir(exist_ok=True)

    def _get_ai_api_key(self) -> str:
        """从环境变量获取AI API密钥"""
        # 优先检查MINIMAX_API_KEY
        minimax_key = os.environ.get('MINIMAX_API_KEY')
        if minimax_key:
            return minimax_key

        # 根据API类型选择环境变量
        if self.ai_api_type == 'claude':
            return os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')
        elif self.ai_api_type == 'openai':
            return os.environ.get('OPENAI_API_KEY')
        elif self.ai_api_type == 'qwen':
            return os.environ.get('DASHSCOPE_API_KEY') or os.environ.get('QWEN_API_KEY')
        elif self.ai_api_type == 'zhipu':
            return os.environ.get('ZHIPU_API_KEY') or os.environ.get('GLM_API_KEY')
        return None

    def _extract_module_name(self, url: str) -> str:
        """从URL提取模块名称"""
        if '/axure/' in url.lower():
            parts = url.split('/')
            for i, part in enumerate(parts):
                if 'axure' in part.lower() and i + 1 < len(parts):
                    module = parts[i + 1].replace('.html', '')
                    import urllib.parse
                    try:
                        module = urllib.parse.unquote(module)
                    except:
                        pass
                    return module
        return "未知模块"

    # ==================== 通用方法 ====================

    def _create_base_image(self, width: int, height: int, title: str,
                          header_color: str = None) -> tuple:
        """创建基础图片的辅助方法

        Returns:
            (img, draw): PIL Image对象和ImageDraw对象
        """
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)

        if header_color:
            draw.rectangle([0, 0, width, 60], fill=header_color)
            draw.text((width // 2 - len(title) * 10, 10), title,
                     font=self.title_font, fill='white')

        return img, draw

    def create_no_info_image(self, filename: str = "不含有效信息_负向.png",
                            module_name: str = "相关信息"):
        """创建不含有效信息的负向测试图片"""
        img = Image.new('RGB', (600, 600), '#f0f0f0')
        draw = ImageDraw.Draw(img)

        draw.ellipse([150, 100, 450, 400], fill='#ffcc00')
        draw.text((220, 220), "风景", font=self.title_font, fill='white')
        draw.text((100, 450), "这是一张风景图片", font=self.text_font, fill='#666')
        draw.text((100, 500), f"不包含{module_name}", font=self.text_font, fill='#666')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def generate_test_description(self, positive_cases: list, negative_cases: list,
                                  ai_features: list = None):
        """生成测试用例说明文件

        Args:
            positive_cases: 正向用例列表 [{'name': '名称', 'desc': '描述', 'data': '测试数据'}]
            negative_cases: 负向用例列表 [{'name': '名称', 'desc': '描述', 'expected': '预期结果'}]
            ai_features: AI功能列表 [{'name': '名称', 'desc': '描述'}]
        """
        content = f"""# {self.module_name}模块测试用例说明

## 模块概述

本模块测试用例基于Axure原型自动生成。

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
原型地址：{self.url}

## 正向测试用例 ({len(positive_cases)}个)

| 编号 | 用例名称 | 测试内容 | 测试数据 |
|------|----------|----------|----------|
"""
        for i, case in enumerate(positive_cases, 1):
            content += f"| {i:02d} | {case.get('name', '用例' + str(i))} | {case.get('desc', '')} | {case.get('data', '-')} |\n"

        content += f"\n## 负向测试用例 ({len(negative_cases)}个)\n\n"
        content += "| 编号 | 用例名称 | 测试内容 | 预期结果 |\n"
        content += "|------|----------|----------|----------|\n"
        for i, case in enumerate(negative_cases, len(positive_cases) + 1):
            content += f"| {i:02d} | {case.get('name', '用例' + str(i))} | {case.get('desc', '')} | {case.get('expected', '-')} |\n"

        if ai_features:
            content += "\n## AI功能说明\n\n"
            for feature in ai_features:
                content += f"### {feature.get('name', '功能')}\n"
                content += f"{feature.get('desc', '')}\n\n"

        content += f"""
## 文件夹结构

```
{self.output_dir.name}/
├── 测试用例说明.txt           # 本文件
├── prototype_overview.png     # 原型概览截图
├── positive/                 # 正向测试用例
│   └── [用例文件夹]/
├── negative/                 # 负向测试用例
│   └── [用例文件夹]/
└── test_data/                # 测试数据图片
    └── [测试数据图片]
```

## 测试数据图片说明

测试数据图片使用PIL生成，身份信息和证件ID使用真实格式：
- 身份证号：110105199001011234（18位标准格式）
- 手机号：13800138000（11位标准格式）
- 不使用星号(*)等遮蔽符号，便于OCR识别测试

## 注意事项

1. 原型截图位于各用例文件夹的 screenshot.png
2. 文本类AI功能配有对应的 .md 文档说明
3. 测试数据图片可直接用于AI对话上传测试
"""

        output_file = self.output_dir / '测试用例说明.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Generated: {output_file.name}")

    # ==================== 出行类测试数据 ====================

    def create_train_ticket(self, filename="01_火车票.png"):
        """生成火车票图片"""
        img = Image.new('RGB', (800, 450), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((250, 10), "火车票", font=self.title_font, fill='white')
        draw.text((50, 80), "G1234", font=self.title_font, fill='#1a5fb4')
        draw.text((400, 80), "2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 140), "出发站：北京南", font=self.text_font, fill='black')
        draw.text((50, 185), "到达站：上海虹桥", font=self.text_font, fill='black')
        draw.text((50, 230), "出发时间：08:30", font=self.text_font, fill='black')
        draw.text((50, 275), "到达时间：12:45", font=self.text_font, fill='black')
        draw.text((50, 320), "票价：553.00元", font=self.text_font, fill='black')
        draw.text((50, 365), "乘客：张三", font=self.text_font, fill='black')
        draw.text((500, 140), "座位：二等座", font=self.text_font, fill='black')
        draw.text((500, 185), "车厢：08车", font=self.text_font, fill='black')
        draw.text((500, 230), "座位号：12A", font=self.text_font, fill='black')
        draw.rectangle([50, 405, 750, 410], fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_flight_ticket(self, filename="02_机票.png"):
        """生成机票图片"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((300, 10), "电子客票", font=self.title_font, fill='white')
        draw.ellipse([50, 80, 150, 180], fill='#26a269')
        draw.text((65, 110), "航班", font=self.text_font, fill='white')
        draw.text((200, 90), "MU5137", font=self.title_font, fill='#1a5fb4')
        draw.text((400, 90), "中国东方航空", font=self.text_font, fill='black')
        draw.text((200, 150), "出发：PEK 北京首都", font=self.text_font, fill='black')
        draw.text((200, 200), "到达：SHA 上海虹桥", font=self.text_font, fill='black')
        draw.text((200, 250), "日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((200, 300), "出发时间：14:30", font=self.text_font, fill='black')
        draw.text((400, 300), "到达时间：16:45", font=self.text_font, fill='black')
        draw.text((500, 150), "乘客：李四", font=self.text_font, fill='black')
        draw.text((500, 200), "舱位：经济舱", font=self.text_font, fill='black')
        draw.text((500, 250), "座位：23K", font=self.text_font, fill='black')
        draw.rectangle([50, 420, 750, 470], fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_taxi_invoice(self, filename="03_打车发票.png"):
        """生成打车发票"""
        img = Image.new('RGB', (600, 800), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 600, 60], fill='#e5a50a')
        draw.text((200, 10), "出租车发票", font=self.title_font, fill='white')
        draw.text((50, 80), "北京出租汽车", font=self.text_font, fill='black')
        draw.text((50, 130), "订单号：TX20260330001", font=self.text_font, fill='black')
        draw.text((50, 180), "上车时间：10:30", font=self.text_font, fill='black')
        draw.text((50, 230), "下车时间：11:15", font=self.text_font, fill='black')
        draw.text((50, 280), "里程：12.5公里", font=self.text_font, fill='black')
        draw.text((50, 330), "等候时间：3分钟", font=self.text_font, fill='black')
        draw.line([50, 380, 550, 380], fill='black', width=2)
        draw.text((50, 400), "金额：45.80元", font=self.title_font, fill='red')
        draw.text((50, 450), "上车地点：朝阳区CBD", font=self.text_font, fill='black')
        draw.text((50, 500), "下车地点：海淀区中关村", font=self.text_font, fill='black')
        draw.rectangle([200, 580, 400, 780], fill='#333')
        draw.text((230, 650), "QR CODE", font=self.text_font, fill='white')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_driving_license(self, filename="04_驾驶证.png"):
        """生成驾驶证"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1c71d8')
        draw.text((280, 10), "驾驶证", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 200, 280], fill='#ddd')
        draw.text((80, 160), "照片", font=self.text_font, fill='#666')
        draw.text((250, 90), "姓名：王五", font=self.text_font, fill='black')
        draw.text((250, 140), "证号：110105199001011234", font=self.text_font, fill='black')
        draw.text((250, 190), "准驾车型：C1", font=self.text_font, fill='black')
        draw.text((250, 240), "有效期：2026-01-01至2036-01-01", font=self.text_font, fill='black')
        draw.text((250, 290), "发证机关：北京市公安局", font=self.text_font, fill='black')
        draw.rectangle([500, 100, 750, 250], fill='#1c71d8')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_walking_record(self, filename="05_步行记录.png"):
        """生成步行记录"""
        img = Image.new('RGB', (600, 700), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 600, 60], fill='#26a269')
        draw.text((220, 10), "健康步行记录", font=self.title_font, fill='white')
        draw.text((50, 80), "2026-03-30 步行记录", font=self.title_font, fill='black')
        draw.text((50, 150), "步数：8,526步", font=self.title_font, fill='#26a269')
        draw.text((50, 220), "距离：6.2公里", font=self.text_font, fill='black')
        draw.text((50, 270), "热量消耗：280千卡", font=self.text_font, fill='black')
        draw.text((50, 320), "活动时间：45分钟", font=self.text_font, fill='black')
        draw.rectangle([50, 380, 550, 600], fill='#e0e0e0')
        draw.text((150, 460), "步行路线示意图", font=self.text_font, fill='#666')
        draw.text((50, 620), "起点：家", font=self.text_font, fill='black')
        draw.text((450, 620), "终点：公园", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_bus_ticket(self, filename="06_汽车票.png"):
        """生成汽车票"""
        img = Image.new('RGB', (700, 350), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 700, 50], fill='#9141ac')
        draw.text((250, 8), "长途汽车客票", font=self.title_font, fill='white')
        draw.text((50, 70), "班次：BJ2026", font=self.text_font, fill='black')
        draw.text((350, 70), "日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 120), "出发：北京站", font=self.text_font, fill='black')
        draw.text((350, 120), "到达：石家庄站", font=self.text_font, fill='black')
        draw.text((50, 170), "发车时间：09:00", font=self.text_font, fill='black')
        draw.text((350, 170), "票价：120.00元", font=self.text_font, fill='black')
        draw.text((50, 220), "乘客：赵六", font=self.text_font, fill='black')
        draw.text((350, 220), "座位：15号", font=self.text_font, fill='black')
        draw.rectangle([50, 280, 650, 330], fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_multiple_records(self, filename="07_多条出行记录.png"):
        """生成多条出行记录"""
        img = Image.new('RGB', (800, 1000), 'white')
        draw = ImageDraw.Draw(img)

        draw.text((250, 20), "出行记录汇总", font=self.title_font, fill='black')

        draw.rectangle([50, 70, 750, 280], outline='#1a5fb4', width=3)
        draw.text((60, 80), "G1234 火车票 - 北京南到上海虹桥", font=self.text_font, fill='#1a5fb4')
        draw.text((60, 130), "2026-03-30", font=self.text_font, fill='black')
        draw.text((60, 170), "出发时间：08:30", font=self.text_font, fill='black')
        draw.text((60, 210), "到达时间：12:45", font=self.text_font, fill='black')
        draw.text((400, 130), "二等座  553元", font=self.text_font, fill='black')

        draw.rectangle([50, 300, 750, 510], outline='#26a269', width=3)
        draw.text((60, 310), "MU5137 机票 - 北京到上海", font=self.text_font, fill='#26a269')
        draw.text((60, 360), "2026-03-30", font=self.text_font, fill='black')
        draw.text((60, 400), "出发时间：14:30", font=self.text_font, fill='black')
        draw.text((60, 440), "到达时间：16:45", font=self.text_font, fill='black')
        draw.text((400, 360), "经济舱", font=self.text_font, fill='black')

        draw.rectangle([50, 530, 750, 740], outline='#e5a50a', width=3)
        draw.text((60, 540), "出租车发票 - 朝阳区到海淀区", font=self.text_font, fill='#e5a50a')
        draw.text((60, 590), "2026-03-30 10:30-11:15  45.80元", font=self.text_font, fill='black')

        draw.rectangle([50, 760, 750, 970], outline='#9141ac', width=3)
        draw.text((60, 770), "BJ2026 汽车票 - 北京站到石家庄站", font=self.text_font, fill='#9141ac')
        draw.text((60, 820), "2026-03-30 09:00  120元", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_no_location_image(self, filename="08_不含地点_美食.png"):
        """生成不含地点的图片"""
        img = Image.new('RGB', (600, 600), '#f0f0f0')
        draw = ImageDraw.Draw(img)

        draw.ellipse([150, 100, 450, 400], fill='#ffcc00')
        draw.text((220, 220), "美食", font=self.title_font, fill='white')
        draw.text((100, 450), "这是一张美食图片", font=self.text_font, fill='#666')
        draw.text((100, 500), "不包含任何地点信息", font=self.text_font, fill='#666')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_inappropriate_content(self, filename="09_不合规内容.png"):
        """生成不合规内容"""
        img = Image.new('RGB', (600, 600), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 600, 80], fill='#c01c28')
        draw.text((150, 20), "内容违规警告", font=self.title_font, fill='white')
        draw.text((50, 120), "根据相关法规：", font=self.text_font, fill='black')
        draw.text((50, 170), "1. 包含暴力或不当内容", font=self.text_font, fill='black')
        draw.text((50, 220), "2. 不适合公开传播", font=self.text_font, fill='black')
        draw.text((50, 270), "3. 违反平台规定", font=self.text_font, fill='black')
        draw.rectangle([100, 350, 500, 450], fill='#e5a50a')
        draw.text((120, 380), "此内容无法记录", font=self.title_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_contract_info(self, filename="10_合同信息.png"):
        """生成合同信息"""
        img = Image.new('RGB', (700, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 700, 50], fill='#1c71d8')
        draw.text((250, 8), "劳动合同", font=self.title_font, fill='white')
        draw.text((50, 70), "甲方：科技有限公司", font=self.text_font, fill='black')
        draw.text((50, 120), "乙方：张三", font=self.text_font, fill='black')
        draw.text((50, 170), "合同期限：2024-01-01至2027-12-31", font=self.text_font, fill='black')
        draw.text((50, 220), "工作岗位：软件工程师", font=self.text_font, fill='black')
        draw.text((50, 270), "月薪：25000元/月", font=self.text_font, fill='black')
        draw.text((50, 320), "合同编号：HT20240101001", font=self.text_font, fill='black')
        draw.rectangle([50, 380, 650, 450], fill='#ddd')
        draw.text((150, 400), "合同章", font=self.text_font, fill='#666')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    # ========== 救助模块测试数据 ==========

    def create_unemployment_certificate(self, filename="01_失业登记证.png"):
        """失业登记证"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((280, 10), "失业登记证", font=self.title_font, fill='white')
        draw.text((50, 80), "姓名：李四", font=self.text_font, fill='black')
        draw.text((400, 80), "证件编号：SY202603300001", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证号：110105199001015678", font=self.text_font, fill='black')
        draw.text((50, 180), "失业日期：2026-03-01", font=self.text_font, fill='black')
        draw.text((50, 230), "失业原因：合同到期", font=self.text_font, fill='black')
        draw.text((50, 280), "登记日期：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 330), "经办机构：北京市朝阳区人社局", font=self.text_font, fill='black')
        draw.text((50, 380), "状态：有效", font=self.title_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_disability_certificate(self, filename="02_残疾证.png"):
        """残疾证"""
        img = Image.new('RGB', (800, 650), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((320, 10), "残疾证", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 200, 280], fill='#ddd')
        draw.text((90, 160), "照片", font=self.text_font, fill='#666')
        draw.text((250, 90), "姓名：王五", font=self.text_font, fill='black')
        draw.text((500, 90), "证号：CZ202603300001", font=self.text_font, fill='black')
        draw.text((250, 140), "残疾类别：肢体残疾", font=self.text_font, fill='black')
        draw.text((500, 140), "残疾等级：二级", font=self.text_font, fill='black')
        draw.text((250, 190), "发证日期：2020-01-01", font=self.text_font, fill='black')
        draw.text((500, 190), "有效期至：2025-01-01", font=self.text_font, fill='black')
        draw.text((250, 240), "发证机关：北京市民政局", font=self.text_font, fill='black')
        draw.rectangle([50, 285, 750, 320], fill='#f0f8f0')
        draw.text((60, 290), "公益救助-活动名称：社区助残志愿服务", font=self.text_font, fill='black')
        draw.rectangle([50, 325, 750, 360], fill='#f0f8f0')
        draw.text((60, 330), "公益救助-参与时间记录：2026-01-15、2026-02-20、2026-03-10", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_social_assistance_form(self, filename="03_社会救助申请审批表.png"):
        """社会救助申请审批表"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((200, 10), "社会救助申请审批表", font=self.title_font, fill='white')
        draw.text((50, 80), "申请人：张三", font=self.text_font, fill='black')
        draw.text((400, 80), "申请日期：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证号：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 180), "家庭住址：北京市朝阳区团结湖街道", font=self.text_font, fill='black')
        draw.text((50, 230), "联系电话：13812345678", font=self.text_font, fill='black')
        draw.text((50, 280), "申请类型：最低生活保障", font=self.text_font, fill='black')
        draw.text((50, 330), "家庭人口：3人", font=self.text_font, fill='black')
        draw.text((50, 380), "月收入：3000元", font=self.text_font, fill='black')
        draw.text((50, 430), "申请理由：因病致贫，生活困难", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_donation_certificate(self, filename="04_公益捐赠证书.png"):
        """公益捐赠证书"""
        img = Image.new('RGB', (700, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 700, 60], fill='#e5a50a')
        draw.text((200, 10), "公益捐赠证书", font=self.title_font, fill='white')
        draw.ellipse([250, 80, 450, 280], fill='#e5a50a')
        draw.text((320, 150), "爱心", font=self.title_font, fill='white')
        draw.text((100, 300), "兹证明：李四", font=self.text_font, fill='black')
        draw.text((100, 350), "于2026-03-20向慈善基金会", font=self.text_font, fill='black')
        draw.text((100, 390), "捐赠人民币：5000元", font=self.title_font, fill='#1a5fb4')
        draw.text((100, 440), "证书编号：ZS202603200001", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    # ========== 养老模块测试数据 ==========

    def create_pension_payment(self, filename="01_养老保险缴费记录.png"):
        """养老保险缴费记录"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((200, 10), "社会保险缴费记录", font=self.title_font, fill='white')
        draw.text((50, 80), "姓名：李四", font=self.text_font, fill='black')
        draw.text((400, 80), "社保账号：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 130), "缴费类型：养老保险", font=self.title_font, fill='#1a5fb4')
        draw.text((50, 180), "缴费起止：2020-01至2026-03", font=self.text_font, fill='black')
        draw.text((400, 180), "发放时间：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 230), "缴费月数：74个月", font=self.text_font, fill='black')
        draw.text((50, 280), "个人缴费：2500元/月", font=self.text_font, fill='black')
        draw.text((50, 330), "单位缴费：5000元/月", font=self.text_font, fill='black')
        draw.text((50, 380), "缴费基数：12500元", font=self.text_font, fill='black')
        draw.text((50, 430), "累计本金：555000元", font=self.title_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return img

    def create_pension_payment_record(self, filename="02_养老金发放记录.png"):
        """养老金发放记录"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((200, 10), "养老金发放记录", font=self.title_font, fill='white')
        draw.text((50, 80), "姓名：王五", font=self.text_font, fill='black')
        draw.text((400, 80), "银行卡号：6222021234567890", font=self.text_font, fill='black')
        draw.text((50, 130), "发放起始：2025-01-01", font=self.text_font, fill='black')
        draw.text((400, 130), "发放时间：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 180), "发放类型：基本养老金", font=self.title_font, fill='#26a269')
        draw.text((50, 230), "月发放金额：4500元", font=self.title_font, fill='green')
        draw.text((50, 280), "已发放月数：15个月", font=self.text_font, fill='black')
        draw.text((50, 330), "累计发放：67500元", font=self.text_font, fill='black')
        draw.text((50, 380), "发放银行：中国建设银行", font=self.text_font, fill='black')
        draw.text((50, 430), "状态：正常发放", font=self.title_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_pension_plan(self, filename="03_养老计划.png"):
        """养老计划"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((250, 10), "个人养老计划", font=self.title_font, fill='white')
        draw.text((50, 80), "制定日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 130), "计划目标：品质养老", font=self.title_font, fill='#9141ac')
        draw.text((50, 180), "目标年龄：60岁", font=self.text_font, fill='black')
        draw.text((50, 230), "距退休：10年", font=self.text_font, fill='black')
        draw.text((50, 280), "月储蓄目标：3000元", font=self.text_font, fill='black')
        draw.text((50, 330), "商业保险：已投保", font=self.text_font, fill='green')
        draw.text((50, 380), "预期养老金：8000元/月", font=self.text_font, fill='black')
        draw.text((50, 430), "养老社区：已预约", font=self.text_font, fill='green')
        draw.text((50, 480), "备注：身体健康，继续工作", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_pension_insurance_card(self, filename="04_社会保障卡.png"):
        """社会保障卡"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1c71d8')
        draw.text((250, 10), "社会保障卡", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 200, 280], fill='#ddd')
        draw.text((80, 160), "照片", font=self.text_font, fill='#666')
        draw.text((250, 90), "姓名：张三", font=self.text_font, fill='black')
        draw.text((500, 90), "社保号：110105199001011234", font=self.text_font, fill='black')
        draw.text((250, 140), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((250, 190), "养老保险：已参保", font=self.text_font, fill='green')
        draw.text((250, 240), "医疗保险：已参保", font=self.text_font, fill='green')
        draw.text((250, 290), "失业保险：已参保", font=self.text_font, fill='green')
        draw.text((250, 340), "发卡银行：中国工商银行", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_pension_bank_flow(self, filename="05_养老金银行流水.png"):
        """养老金银行流水"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((200, 10), "养老金银行流水", font=self.title_font, fill='white')
        draw.text((50, 80), "交易日期    交易描述        金额", font=self.text_font, fill='black')
        draw.line([50, 110, 750, 110], fill='black')

        transactions = [
            ("2026-01-05", "养老金发放", "+4500.00"),
            ("2026-02-05", "养老金发放", "+4500.00"),
            ("2026-02-10", "消费", "-200.00"),
            ("2026-03-05", "养老金发放", "+4500.00"),
            ("2026-03-15", "消费", "-150.00"),
        ]

        y = 130
        for date, desc, amount in transactions:
            color = 'black' if '-' in amount else 'green'
            draw.text((50, y), f"{date}    {desc}        {amount}", font=self.text_font, fill=color)
            y += 50

        draw.line([50, y+10, 750, y+10], fill='black')
        draw.text((50, y+30), "本月收入：9000.00元    本月支出：350.00元", font=self.text_font, fill='black')
        draw.text((50, y+80), "账户余额：25150.00元", font=self.title_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    # ========== 时间轴模块测试数据 ==========

    def create_text_record(self, filename="01_文本记录_正常.png"):
        """时间轴文本记录"""
        img = Image.new('RGB', (800, 400), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((250, 10), "时间轴记录", font=self.title_font, fill='white')
        draw.text((50, 80), "标题：2026年春节", font=self.text_font, fill='black')
        draw.text((50, 130), "日期：2026-01-28", font=self.text_font, fill='black')
        draw.text((50, 180), "地点：北京", font=self.text_font, fill='black')
        draw.text((50, 230), "内容：春节期间在北京与家人团聚，", font=self.text_font, fill='black')
        draw.text((50, 270), "游览了故宫和长城。", font=self.text_font, fill='black')
        draw.text((50, 320), "标签：旅行,家庭", font=self.text_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_ai_polish_result(self, filename="02_AI润色_正常.png"):
        """AI润色结果"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((250, 10), "AI润色结果", font=self.title_font, fill='white')
        draw.text((50, 80), "原始文本：", font=self.text_font, fill='#666')
        draw.text((50, 110), "今天去北京玩很开心。故宫很大，长城很长。", font=self.text_font, fill='black')
        draw.line([50, 150, 750, 150], fill='#ccc', width=2)
        draw.text((50, 170), "润色后：", font=self.text_font, fill='green')
        draw.text((50, 210), "大年初一，我与家人一同前往北京，", font=self.text_font, fill='black')
        draw.text((50, 250), "游览了气势恢宏的故宫与绵延起伏的长城，", font=self.text_font, fill='black')
        draw.text((50, 290), "度过了愉快而难忘的春节假期。", font=self.text_font, fill='black')
        draw.text((50, 340), "润色类型：正式书面", font=self.text_font, fill='blue')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_ai_expand_result(self, filename="03_AI扩写_正常.png"):
        """AI扩写结果"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((250, 10), "AI扩写结果", font=self.title_font, fill='white')
        draw.text((50, 80), "原始文本：", font=self.text_font, fill='#666')
        draw.text((50, 110), "今天去颐和园散步。", font=self.text_font, fill='black')
        draw.line([50, 150, 750, 150], fill='#ccc', width=2)
        draw.text((50, 170), "扩写后：", font=self.text_font, fill='#9141ac')
        draw.text((50, 210), "春日午后，阳光和煦。我独自漫步于颐和园昆明湖畔，", font=self.text_font, fill='black')
        draw.text((50, 250), "长廊画栋雕梁，湖光潋滟，远山如黛。", font=self.text_font, fill='black')
        draw.text((50, 290), "微风拂面，柳丝轻摇，心旷神怡，流连忘返。", font=self.text_font, fill='black')
        draw.text((50, 340), "扩写风格：文学散文", font=self.text_font, fill='blue')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_ai_summarize_result(self, filename="04_AI缩写_正常.png"):
        """AI缩写结果"""
        img = Image.new('RGB', (800, 400), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#c01c28')
        draw.text((280, 10), "AI缩写结果", font=self.title_font, fill='white')
        draw.text((50, 80), "原始文本：", font=self.text_font, fill='#666')
        draw.text((50, 110), "今天上午9点从家里出发，开了30分钟的车，", font=self.text_font, fill='black')
        draw.text((50, 140), "10点到公司，先开了个晨会，然后处理邮件，", font=self.text_font, fill='black')
        draw.text((50, 170), "中午12点在食堂吃饭，下午继续工作，6点下班回家。", font=self.text_font, fill='black')
        draw.line([50, 210, 750, 210], fill='#ccc', width=2)
        draw.text((50, 225), "缩写后：", font=self.text_font, fill='#c01c28')
        draw.text((50, 255), "上午通勤办公，午间用餐，下午继续工作，傍晚返家。", font=self.text_font, fill='black')
        draw.text((50, 300), "缩写风格：简洁摘要", font=self.text_font, fill='blue')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_ai_privacy_result(self, filename="05_AI隐私保护_正常.png"):
        """AI隐私保护结果"""
        img = Image.new('RGB', (800, 450), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1c71d8')
        draw.text((220, 10), "AI隐私保护结果", font=self.title_font, fill='white')
        draw.text((50, 80), "原始文本：", font=self.text_font, fill='#666')
        draw.text((50, 110), "张三的身份证号是110105199001011234，", font=self.text_font, fill='black')
        draw.text((50, 140), "手机号13800138000，住址为北京市朝阳区某路1号。", font=self.text_font, fill='black')
        draw.line([50, 180, 750, 180], fill='#ccc', width=2)
        draw.text((50, 195), "隐私保护后：", font=self.text_font, fill='green')
        draw.text((50, 225), "[姓名]的身份证号是[身份证号]，", font=self.text_font, fill='black')
        draw.text((50, 255), "手机号[手机号]，住址为[详细地址已隐藏]。", font=self.text_font, fill='black')
        draw.text((50, 300), "已识别：姓名(1) | 身份证(1) | 手机号(1) | 地址(1)", font=self.text_font, fill='blue')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_image_to_text(self, filename="07_图生文_正常.png"):
        """图生文结果"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((200, 10), "图片描述生成", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 350, 380], fill='#ddd')
        draw.text((140, 200), "上传图片", font=self.text_font, fill='#666')
        draw.line([50, 410, 750, 410], fill='#ccc', width=2)
        draw.text((50, 425), "AI描述：", font=self.text_font, fill='#9141ac')
        draw.text((50, 455), "照片摄于颐和园昆明湖畔，远处可见佛香阁，", font=self.text_font, fill='black')
        draw.text((50, 480), "湖面波光粼粼，游客漫步其间，整体氛围宁静祥和。", font=self.text_font, fill='black')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_video_image_record(self, filename="06_视频图片记录_正常.png"):
        """视频图片记录"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((220, 10), "视频/图片记录", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 350, 380], fill='#333')
        draw.text((130, 200), "视频封面", font=self.text_font, fill='white')
        draw.text((60, 390), "视频时长：02:35", font=self.text_font, fill='black')
        draw.rectangle([420, 80, 750, 380], fill='#ddd')
        draw.text((520, 200), "图片1", font=self.text_font, fill='#666')
        draw.text((420, 390), "图片2", font=self.text_font, fill='black')
        draw.text((50, 430), "标题：2026年春节旅行记录", font=self.text_font, fill='black')
        draw.text((50, 480), "日期：2026-01-28    地点：北京故宫", font=self.text_font, fill='black')
        draw.text((50, 530), "AI生成描述：古建筑群壮观，红墙金瓦，年味十足", font=self.text_font, fill='green')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_short_text_negative(self, filename="10_文本过短_负向.png"):
        """文本过短无法处理（负向）"""
        img = Image.new('RGB', (800, 400), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((220, 10), "文本过短-无法润色", font=self.title_font, fill='white')
        draw.text((50, 80), "输入文本：", font=self.text_font, fill='#666')
        draw.text((50, 120), "好", font=self.title_font, fill='black')
        draw.rectangle([50, 160, 750, 220], outline='#c01c28', width=2)
        draw.text((100, 170), "错误：文本过短，无法进行AI润色", font=self.text_font, fill='#c01c28')
        draw.text((50, 240), "提示：润色需要至少10个字符", font=self.text_font, fill='#666')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_inappropriate_text_negative(self, filename="11_内容不合规_负向.png"):
        """内容不合规（负向）"""
        img = Image.new('RGB', (800, 400), 'white')
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 800, 60], fill='#c01c28')
        draw.text((220, 10), "内容不合规", font=self.title_font, fill='white')
        draw.text((50, 80), "输入内容检测中...", font=self.text_font, fill='black')
        draw.rectangle([50, 130, 750, 200], outline='#c01c28', width=2)
        draw.text((100, 140), "内容不合规，无法添加至时间轴", font=self.text_font, fill='#c01c28')
        draw.text((50, 220), "原因：内容包含违规信息", font=self.text_font, fill='#666')

        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def generate_travel_test_data(self):
        """生成出行模块的测试数据"""
        images = [
            self.create_train_ticket(),
            self.create_flight_ticket(),
            self.create_taxi_invoice(),
            self.create_driving_license(),
            self.create_walking_record(),
            self.create_bus_ticket(),
            self.create_multiple_records(),
            self.create_no_location_image(),
            self.create_inappropriate_content(),
        ]
        print(f"Generated {len(images)} travel test data images")
        return images

    def generate_timeline_test_data(self):
        """生成时间轴模块的测试数据"""
        images = [
            self.create_text_record(),
            self.create_ai_polish_result(),
            self.create_ai_expand_result(),
            self.create_ai_summarize_result(),
            self.create_ai_privacy_result(),
            self.create_video_image_record(),
            self.create_image_to_text(),
            self.create_short_text_negative(),
            self.create_inappropriate_text_negative(),
            self.create_no_info_image(module_name="时间轴相关信息"),
        ]
        print(f"Generated {len(images)} timeline test data images")
        return images

    def generate_marriage_test_data(self):
        """生成婚育模块的测试数据"""
        images = []
        if self.use_ai:
            # 使用AI生成逼真图片
            self.generate_ai_image('marriage_certificate', '01_结婚证.png')
            self.generate_ai_image('divorce_certificate', '02_离婚证.png')
            self.generate_ai_image('birth_certificate', '04_出生医学证明.png')
            self.create_no_info_image(module_name="婚育相关信息")
            images = ['01_结婚证.png', '02_离婚证.png', '04_出生医学证明.png', '不含有效信息_负向.png']
        else:
            # 使用PIL生成简单图片
            images = [
                self.create_marriage_certificate_v2(),
                self.create_divorce_certificate_v2(),
                self.create_birth_certificate_v2(),
                self.create_antenatal_report(),
                self.create_hukou_book(),
                self.create_settlement_certificate(),
                self.create_fertility_registration(),
                self.create_no_info_image(module_name="婚育相关信息"),
            ]
        print(f"Generated {len(images)} marriage test data images")
        return images

    def generate_behind_test_data(self):
        """生成身后模块的测试数据"""
        images = []
        if self.use_ai:
            # 使用AI生成逼真图片
            self.generate_ai_image('will_notary', '01_遗嘱公证书.png')
            self.generate_ai_image('death_certificate', '03_死亡医学证明.png')
            self.create_no_info_image(module_name="身后相关信息")
            images = ['01_遗嘱公证书.png', '03_死亡医学证明.png', '不含有效信息_负向.png']
        else:
            # 使用PIL生成简单图片
            images = [
                self.create_will_notary(),
                self.create_bequest_agreement(),
                self.create_death_certificate_v2(),
                self.create_cremation_certificate(),
                self.create_self_written_will(),
                self.create_no_info_image(module_name="身后相关信息"),
            ]
        print(f"Generated {len(images)} behind test data images")
        return images

    def generate_travel_test_data(self):
        """生成出行模块的测试数据"""
        images = []
        if self.use_ai:
            # 使用AI生成逼真图片
            self.generate_ai_image('train_ticket', '01_火车票.png')
            self.generate_ai_image('flight_ticket', '02_机票.png')
            self.generate_ai_image('taxi_invoice', '03_打车发票.png')
            self.generate_ai_image('driving_license', '04_驾驶证.png')
            self.create_no_info_image(module_name="出行相关信息")
            images = ['01_火车票.png', '02_机票.png', '03_打车发票.png', '04_驾驶证.png', '不含有效信息_负向.png']
        else:
            # 使用PIL生成简单图片
            images = [
                self.create_train_ticket(),
                self.create_flight_ticket(),
                self.create_taxi_invoice(),
                self.create_driving_license(),
                self.create_walking_record(),
                self.create_bus_ticket(),
                self.create_multiple_records(),
                self.create_no_location_image(),
                self.create_inappropriate_content(),
            ]
        print(f"Generated {len(images)} travel test data images")
        return images

    def generate_commute_test_data(self):
        """生成出勤模块的测试数据（健康报告、求职登记、出行记录等）

        使用分层合成方案：
        1. AI生成无文字的视觉背景（质感、印章、装饰）
        2. PIL渲染正确的中文叠加在上层
        3. 合成得到：AI视觉质感 + 正确汉字
        """
        if self.use_ai:
            print("Using AI composite generation (background + PIL text overlay)...")

            # 正向用例
            self.generate_ai_image('health_report', '01_健康信息_正常.png',
                                   custom_params={'date': '2026-03-28'})
            self.generate_ai_image('job_registration', '02_求职登记_正常.png')
            self.generate_ai_image('flight_ticket', '03_飞机行程_正常.png',
                                   custom_params={'date': '2026-03-28'})
            self.generate_ai_image('map_screenshot', '04_自驾出行_正常.png')
            self.generate_ai_image('taxi_invoice', '05_打车发票_正常.png',
                                   custom_params={'date': '2026-03-28'})
            self.generate_ai_image('travel_record', '06_出行记录_正常.png',
                                   custom_params={'date': '2026-03-28'})
            self.generate_ai_image('supplementary', '07_Supplementary_正常.png')
            self.generate_ai_image('multiple_records', '08_多条记录_正常.png',
                                   custom_params={'date': '2026-03-28'})

            # 负向用例
            self.generate_ai_image('no_info', '09_不含有效信息_负向.png')
            self.generate_ai_image('warning_message', '10_内容不合规_负向.png')
            self.generate_ai_image('network_error', '11_网络异常_负向.png')
            self.generate_ai_image('cancel_operation', '12_取消操作_负向.png')
        else:
            # 使用PIL生成简单图片
            self._create_pil_health_report().save(self.output_dir / 'test_data' / '01_健康信息_正常.png')
            self._create_pil_job_registration().save(self.output_dir / 'test_data' / '02_求职登记_正常.png')
            self._create_pil_flight_ticket().save(self.output_dir / 'test_data' / '03_飞机行程_正常.png')
            self._create_pil_map_screenshot().save(self.output_dir / 'test_data' / '04_自驾出行_正常.png')
            self._create_pil_taxi_invoice().save(self.output_dir / 'test_data' / '05_打车发票_正常.png')
            self._create_pil_app_screenshot().save(self.output_dir / 'test_data' / '06_出行记录_正常.png')
            self._create_pil_supplementary().save(self.output_dir / 'test_data' / '07_Supplementary_正常.png')
            self._create_pil_multiple_records().save(self.output_dir / 'test_data' / '08_多条记录_正常.png')
            self._create_pil_no_info_image().save(self.output_dir / 'test_data' / '09_不含有效信息_负向.png')
            self._create_pil_warning_message().save(self.output_dir / 'test_data' / '10_内容不合规_负向.png')
            self._create_pil_network_error().save(self.output_dir / 'test_data' / '11_网络异常_负向.png')
            self._create_pil_cancel_operation().save(self.output_dir / 'test_data' / '12_取消操作_负向.png')

        print("Generated commute test data images")

    def generate_timeline_test_data(self):
        """生成时间轴模块的测试数据"""
        images = []
        if self.use_ai:
            # 使用AI生成逼真图片
            self.generate_ai_image('text_record', '01_文本记录_正常.png')
            self.generate_ai_image('ai_polish', '02_AI润色_正常.png')
            self.create_no_info_image(module_name="时间轴相关信息")
            images = ['01_文本记录_正常.png', '02_AI润色_正常.png', '不含有效信息_负向.png']
        else:
            # 使用PIL生成简单图片
            images = [
                self.create_text_record(),
                self.create_ai_polish_result(),
                self.create_ai_expand_result(),
                self.create_ai_summarize_result(),
                self.create_ai_privacy_result(),
                self.create_video_image_record(),
                self.create_image_to_text(),
                self.create_short_text_negative(),
                self.create_inappropriate_text_negative(),
                self.create_no_info_image(module_name="时间轴相关信息"),
            ]
        print(f"Generated {len(images)} timeline test data images")
        return images

    def generate_pension_test_data(self):
        """生成养老模块的测试数据"""
        images = []
        if self.use_ai:
            # 使用AI生成逼真图片
            self.generate_ai_image('pension_record', '01_养老保险缴费记录.png')
            self.create_no_info_image(module_name="养老相关信息")
            images = ['01_养老保险缴费记录.png', '不含有效信息_负向.png']
        else:
            # 使用PIL生成简单图片
            images = [
                self.create_pension_payment(),
                self.create_pension_payment_record(),
                self.create_pension_plan(),
                self.create_pension_insurance_card(),
                self.create_pension_bank_flow(),
                self.create_no_info_image(module_name="养老相关信息"),
            ]
        print(f"Generated {len(images)} pension test data images")
        return images

    def generate_notary_test_data(self):
        """生成公证智能体模块的测试数据"""
        images = []
        if self.use_ai:
            print("Using AI to generate realistic images...")
        else:
            print("Using PIL to generate simple images...")

        # 使用PIL生成公证相关测试图片
        images = [
            self.create_id_card(),
            self.create_business_license(),
            self.create_data_asset_report(),
            self.create_data_asset_certificate(),
            self.create_notary_certificate(),
            self.create_no_info_image(module_name="公证相关信息"),
        ]
        print(f"Generated {len(images)} notary test data images")
        return images

    def create_id_card(self, filename="01_身份证.png"):
        """身份证"""
        img = Image.new('RGB', (900, 600), 'white')
        draw = ImageDraw.Draw(img)
        # 正面
        draw.rectangle([0, 0, 900, 600], fill='#1a5490')
        draw.text((80, 30), "中华人民共和国居民身份证", font=self.title_font, fill='white')
        draw.rectangle([580, 80, 860, 540], fill='#ddd')
        draw.text((665, 280), "照片", font=self.text_font, fill='#666')
        draw.text((80, 100), "姓名：张三", font=self.text_font, fill='white')
        draw.text((80, 150), "性别：男", font=self.text_font, fill='white')
        draw.text((80, 200), "民族：汉族", font=self.text_font, fill='white')
        draw.text((80, 250), "出生：1990-01-01", font=self.text_font, fill='white')
        draw.text((80, 310), "住址：北京市朝阳区", font=self.small_font, fill='white')
        draw.text((80, 350), "建国路88号1号楼101室", font=self.small_font, fill='white')
        draw.text((80, 400), "公民身份号码", font=self.text_font, fill='white')
        draw.text((80, 440), "110105199001011234", font=self.title_font, fill='#ffff00')
        draw.text((80, 500), "签发机关：北京市公安局", font=self.text_font, fill='white')
        draw.text((80, 540), "有效期限：2020.01.01-2030.01.01", font=self.text_font, fill='white')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_business_license(self, filename="02_营业执照.png"):
        """营业执照"""
        img = Image.new('RGB', (800, 1000), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 80], fill='#c01c28')
        draw.text((230, 15), "营业执照", font=self.title_font, fill='white')
        draw.text((100, 100), "统一社会信用代码", font=self.text_font, fill='black')
        draw.text((100, 140), "91110000MA01ABCD23", font=self.title_font, fill='black')
        draw.text((100, 190), "名称：北京数据科技有限公司", font=self.text_font, fill='black')
        draw.text((100, 240), "类型：有限责任公司", font=self.text_font, fill='black')
        draw.text((100, 290), "住所：北京市海淀区中关村大街1号", font=self.text_font, fill='black')
        draw.text((100, 340), "法定代表人：张三", font=self.text_font, fill='black')
        draw.text((100, 390), "注册资本：1000万元人民币", font=self.text_font, fill='black')
        draw.text((100, 440), "成立日期：2020-05-20", font=self.text_font, fill='black')
        draw.text((100, 490), "营业期限：2020-05-20至长期", font=self.text_font, fill='black')
        draw.text((100, 540), "经营范围：数据资产服务、技术开发", font=self.text_font, fill='black')
        draw.text((100, 590), "登记机关：北京市市场监督管理局", font=self.text_font, fill='black')
        draw.rectangle([250, 920, 550, 960], fill='#ddd')
        draw.text((265, 928), "北京市市场监督管理局", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_data_asset_report(self, filename="03_数据资产报告.png"):
        """数据资产报告"""
        img = Image.new('RGB', (800, 1000), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 80], fill='#1a5490')
        draw.text((230, 15), "数据资产登记报告", font=self.title_font, fill='white')
        draw.text((80, 100), "报告编号：DARS2026050001", font=self.text_font, fill='black')
        draw.text((80, 150), "数据资产名称：用户行为分析数据集", font=self.text_font, fill='black')
        draw.text((80, 200), "权利人：北京数据科技有限公司", font=self.text_font, fill='black')
        draw.text((80, 250), "登记日期：2026-05-01", font=self.text_font, fill='black')
        draw.text((80, 300), "数据量级：1000万条", font=self.text_font, fill='black')
        draw.text((80, 350), "数据分类：商业数据-用户行为", font=self.text_font, fill='black')
        draw.text((80, 400), "存储方式：分布式数据库", font=self.text_font, fill='black')
        draw.text((80, 450), "数据质量评分：95分", font=self.text_font, fill='black')
        draw.text((80, 500), "安全等级：二级", font=self.text_font, fill='black')
        draw.text((80, 550), "资产评估价值：500万元", font=self.text_font, fill='black')
        draw.text((80, 610), "报告机构：北京数据资产登记中心", font=self.text_font, fill='black')
        draw.text((80, 650), "评估日期：2026-05-01", font=self.text_font, fill='black')
        draw.rectangle([200, 900, 600, 940], fill='#ddd')
        draw.text((245, 908), "数据资产登记专用章", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_data_asset_certificate(self, filename="04_数据资产证书.png"):
        """数据资产登记证书"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 70], fill='#1a5490')
        draw.text((250, 12), "数据资产登记证书", font=self.title_font, fill='white')
        draw.text((80, 100), "证书编号：DAC20260500001", font=self.text_font, fill='black')
        draw.text((80, 150), "数据资产名称", font=self.text_font, fill='black')
        draw.text((80, 190), "用户行为分析数据集", font=self.title_font, fill='black')
        draw.text((80, 250), "权利人：北京数据科技有限公司", font=self.text_font, fill='black')
        draw.text((80, 300), "登记日期：2026-05-01", font=self.text_font, fill='black')
        draw.text((80, 350), "有效期至：2027-05-01", font=self.text_font, fill='black')
        draw.text((80, 400), "登记机构：北京数据资产登记中心", font=self.text_font, fill='black')
        draw.rectangle([200, 500, 600, 540], fill='#ddd')
        draw.text((230, 508), "数据资产登记专用章", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_notary_certificate(self, filename="05_公证员执业证书.png"):
        """公证员执业证书"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 70], fill='#c01c28')
        draw.text((260, 12), "公证员执业证书", font=self.title_font, fill='white')
        draw.text((80, 100), "证书编号：GZZS110101001", font=self.text_font, fill='black')
        draw.text((80, 150), "姓名：李明", font=self.title_font, fill='black')
        draw.text((80, 210), "性别：男", font=self.text_font, fill='black')
        draw.text((80, 260), "执业机构：北京市公证处", font=self.text_font, fill='black')
        draw.text((80, 310), "执业证号：110101001001", font=self.text_font, fill='black')
        draw.text((80, 360), "执业范围：国内公证", font=self.text_font, fill='black')
        draw.text((80, 410), "发证日期：2020-01-01", font=self.text_font, fill='black')
        draw.text((80, 450), "有效期至：2025-01-01", font=self.text_font, fill='black')
        draw.text((80, 500), "司法行政机关：北京市司法局", font=self.text_font, fill='black')
        draw.rectangle([200, 500, 600, 540], fill='#ddd')
        draw.text((230, 508), "北京市公证员协会", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    # ========== 婚育类测试数据（新版）==========

    def create_marriage_certificate_v2(self, filename="01_结婚证.png"):
        """结婚证"""
        img = Image.new('RGB', (1000, 750), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1000, 65], fill='#c01c28')
        draw.text((390, 12), "结婚证", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 230, 290], fill='#ddd')
        draw.text((115, 165), "照片", font=self.text_font, fill='#666')
        draw.rectangle([270, 80, 450, 290], fill='#ddd')
        draw.text((335, 165), "照片", font=self.text_font, fill='#666')
        # 夫方信息
        draw.text((50, 305), "夫：张三", font=self.text_font, fill='black')
        draw.text((50, 345), "出生日期：1990-01-01", font=self.text_font, fill='black')
        draw.text((50, 385), "民族：汉族", font=self.text_font, fill='black')
        draw.text((50, 425), "户籍所在地：北京市朝阳区", font=self.text_font, fill='black')
        draw.text((50, 465), "身份证：110105199001011234", font=self.text_font, fill='black')
        # 妻方信息
        draw.text((520, 305), "妻：李四", font=self.text_font, fill='black')
        draw.text((520, 345), "出生日期：1995-05-15", font=self.text_font, fill='black')
        draw.text((520, 385), "民族：汉族", font=self.text_font, fill='black')
        draw.text((520, 425), "户籍所在地：上海市浦东新区", font=self.text_font, fill='black')
        draw.text((520, 465), "身份证：110105199501015678", font=self.text_font, fill='black')
        # 共同信息
        draw.text((50, 515), "登记日期：2020-05-20", font=self.text_font, fill='black')
        draw.text((520, 515), "登记机关：北京市民政局", font=self.text_font, fill='black')
        draw.text((50, 555), "结婚证号：J202005200001", font=self.text_font, fill='black')
        draw.rectangle([50, 600, 950, 640], fill='#ddd')
        draw.text((245, 605), "中华人民共和国婚姻登记专用章", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_divorce_certificate_v2(self, filename="02_离婚证.png"):
        """离婚证"""
        img = Image.new('RGB', (900, 650), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 900, 60], fill='#1a5fb4')
        draw.text((330, 10), "离婚证", font=self.title_font, fill='white')
        # 左列
        draw.text((50, 80), "姓名：张三", font=self.text_font, fill='black')
        draw.text((50, 130), "性别：男", font=self.text_font, fill='black')
        draw.text((50, 180), "出生日期：1990-01-01", font=self.text_font, fill='black')
        draw.text((50, 230), "民族：汉族", font=self.text_font, fill='black')
        draw.text((50, 280), "户籍：北京市朝阳区", font=self.text_font, fill='black')
        draw.text((50, 330), "所在地：北京市朝阳区建国路88号", font=self.text_font, fill='black')
        # 右列
        draw.text((480, 80), "证号：L20260301001", font=self.text_font, fill='black')
        draw.text((480, 130), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((480, 180), "登记日期：2020-05-20", font=self.text_font, fill='black')
        draw.text((480, 230), "离婚日期：2026-03-01", font=self.text_font, fill='black')
        draw.text((480, 280), "离婚方式：协议离婚", font=self.text_font, fill='black')
        draw.text((480, 330), "子女抚养：已协商", font=self.text_font, fill='black')
        draw.text((480, 380), "登记机关：北京市民政局", font=self.text_font, fill='black')
        draw.rectangle([50, 570, 850, 620], fill='#ddd')
        draw.text((200, 585), "离婚登记专用章", font=self.text_font, fill='#1a5fb4')
        img.save(self.output_dir / 'test_data' / filename)
        return filename
        return filename

    def create_birth_certificate_v2(self, filename="04_出生医学证明.png"):
        """出生医学证明"""
        img = Image.new('RGB', (800, 550), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#1c71d8')
        draw.text((200, 10), "出生医学证明", font=self.title_font, fill='white')
        draw.text((50, 80), "新生儿姓名：张小一", font=self.text_font, fill='black')
        draw.text((400, 80), "编号：CS20260315001", font=self.text_font, fill='black')
        draw.text((50, 130), "性别：男", font=self.text_font, fill='black')
        draw.text((400, 130), "出生体重：3500克", font=self.text_font, fill='black')
        draw.text((50, 180), "出生日期：2026-01-15 10:30", font=self.text_font, fill='black')
        draw.text((50, 230), "出生医院：北京市妇幼保健院", font=self.text_font, fill='black')
        draw.text((50, 280), "母亲姓名：李四", font=self.text_font, fill='black')
        draw.text((50, 330), "母亲身份证：110105199501015678", font=self.text_font, fill='black')
        draw.text((50, 380), "父亲姓名：张三", font=self.text_font, fill='black')
        draw.text((50, 430), "父亲身份证：110105199001011234", font=self.text_font, fill='black')
        draw.rectangle([50, 480, 750, 530], fill='#ddd')
        draw.text((150, 495), "出生医学证明专用章", font=self.text_font, fill='#666')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_antenatal_report(self, filename="05_产检报告.png"):
        """产检报告"""
        img = Image.new('RGB', (800, 650), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((250, 10), "产前检查报告", font=self.title_font, fill='white')
        draw.text((50, 80), "孕妇姓名：李四", font=self.text_font, fill='black')
        draw.text((400, 80), "报告编号：CJ20260301001", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证：110105199501015678", font=self.text_font, fill='black')
        draw.text((50, 180), "孕周：第12周", font=self.text_font, fill='black')
        draw.text((50, 230), "检查日期：2026-01-10", font=self.text_font, fill='black')
        draw.text((400, 230), "产检时间：09:30", font=self.text_font, fill='black')
        draw.text((50, 280), "检查医院：北京市妇幼保健院", font=self.text_font, fill='black')
        draw.text((50, 330), "检查项目：血常规、尿常规、B超", font=self.text_font, fill='black')
        draw.text((50, 380), "检查结果：正常", font=self.text_font, fill='green')
        draw.text((50, 430), "医生建议：定期产检，注意营养", font=self.text_font, fill='black')
        draw.text((50, 480), "主治医师：王医生", font=self.text_font, fill='black')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_hukou_book(self, filename="06_户口本.png"):
        """户口本"""
        img = Image.new('RGB', (700, 950), 'white')
        draw = ImageDraw.Draw(img)
        # 封面
        draw.rectangle([0, 0, 700, 60], fill='#1a5fb4')
        draw.text((220, 10), "中华人民共和国", font=self.title_font, fill='white')
        draw.text((250, 50), "户口簿", font=self.title_font, fill='white')
        draw.rectangle([50, 90, 650, 130], fill='#ddd')
        draw.text((80, 95), "户号：110105001001", font=self.text_font, fill='black')
        draw.text((420, 95), "户主：张三", font=self.text_font, fill='black')
        # 表头
        draw.rectangle([50, 140, 650, 175], fill='#1a5fb4')
        draw.text((60, 142), "姓名", font=self.small_font, fill='white')
        draw.text((160, 142), "关系", font=self.small_font, fill='white')
        draw.text((250, 142), "出生日期", font=self.small_font, fill='white')
        draw.text((370, 142), "身份证", font=self.small_font, fill='white')
        draw.text((530, 142), "民族", font=self.small_font, fill='white')
        # 人员1
        draw.rectangle([50, 175, 650, 210], fill='#f8f8f8')
        draw.text((70, 178), "张三", font=self.small_font, fill='black')
        draw.text((165, 178), "户主", font=self.small_font, fill='black')
        draw.text((260, 178), "1990-01-01", font=self.small_font, fill='black')
        draw.text((340, 178), "110105199001011234", font=self.small_font, fill='black')
        draw.text((545, 178), "汉族", font=self.small_font, fill='black')
        # 人员2
        draw.rectangle([50, 210, 650, 245], fill='white')
        draw.text((70, 213), "李四", font=self.small_font, fill='black')
        draw.text((165, 213), "配偶", font=self.small_font, fill='black')
        draw.text((260, 213), "1995-05-15", font=self.small_font, fill='black')
        draw.text((340, 213), "110105199501015678", font=self.small_font, fill='black')
        draw.text((545, 213), "汉族", font=self.small_font, fill='black')
        # 人员3
        draw.rectangle([50, 245, 650, 280], fill='#f8f8f8')
        draw.text((70, 248), "张小一", font=self.small_font, fill='black')
        draw.text((165, 248), "子女", font=self.small_font, fill='black')
        draw.text((260, 248), "2026-01-15", font=self.small_font, fill='black')
        draw.text((340, 248), "110105202601150010", font=self.small_font, fill='black')
        draw.text((545, 248), "汉族", font=self.small_font, fill='black')
        # 地址信息
        draw.rectangle([50, 290, 650, 350], fill='white')
        draw.text((60, 298), "住址：北京市朝阳区建国路88号1号楼101室", font=self.text_font, fill='black')
        draw.text((60, 333), "本户人数：3人", font=self.text_font, fill='black')
        # 登记信息
        draw.rectangle([50, 360, 650, 395], fill='#ddd')
        draw.text((60, 365), "发证日期：2020-05-20    登记机关：北京市公安局朝阳分局", font=self.small_font, fill='black')
        # 变更记录
        draw.rectangle([50, 405, 650, 440], fill='#1a5fb4')
        draw.text((60, 408), "变更记录", font=self.small_font, fill='white')
        draw.rectangle([50, 440, 650, 475], fill='#f8f8f8')
        draw.text((60, 443), "2020-05-20    新立户", font=self.small_font, fill='black')
        draw.rectangle([50, 475, 650, 510], fill='white')
        draw.text((60, 478), "2026-01-15    子女出生登记（张小一）", font=self.small_font, fill='black')
        draw.rectangle([50, 510, 650, 545], fill='#f8f8f8')
        draw.text((60, 513), "2026-03-30    婚姻状况变更（李四迁入）", font=self.small_font, fill='black')
        # 签章
        draw.rectangle([50, 870, 650, 920], fill='#ddd')
        draw.text((180, 875), "北京市公安局朝阳分局户口专用章", font=self.text_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_settlement_certificate(self, filename="07_落户证明.png"):
        """落户证明"""
        img = Image.new('RGB', (800, 700), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 65], fill='#1a5fb4')
        draw.text((250, 10), "落户证明", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 750, 130], fill='#f0f4ff')
        draw.text((60, 88), "编号：LH202603300001", font=self.text_font, fill='black')
        draw.text((500, 88), "日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 145), "申请人姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 145), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 195), "原户籍地：北京市朝阳区", font=self.text_font, fill='black')
        draw.text((400, 195), "联系电话：13800138000", font=self.text_font, fill='black')
        draw.text((50, 245), "落户地址：北京市海淀区中关村大街1号", font=self.text_font, fill='black')
        draw.text((400, 245), "户籍性质：城镇户口", font=self.text_font, fill='black')
        draw.text((50, 295), "落户类型：人才引进", font=self.text_font, fill='black')
        draw.text((400, 295), "申请日期：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 345), "审批状态：已通过", font=self.title_font, fill='green')
        draw.text((400, 345), "审批日期：2026-03-25", font=self.text_font, fill='black')
        draw.text((50, 395), "审批机关：北京市海淀区公安分局", font=self.text_font, fill='black')
        draw.text((50, 445), "承办人：刘警官", font=self.text_font, fill='black')
        draw.rectangle([50, 500, 750, 660], fill='#ddd')
        draw.text((150, 505), "北京市海淀区公安分局", font=self.text_font, fill='#c01c28')
        draw.text((150, 545), "落户审批专用章", font=self.small_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_fertility_registration(self, filename="08_生育登记.png"):
        """生育登记"""
        img = Image.new('RGB', (800, 650), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 65], fill='#26a269')
        draw.text((250, 10), "生育登记服务单", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 750, 130], fill='#f0f8f0')
        draw.text((60, 88), "登记编号：SY202603300001", font=self.text_font, fill='black')
        draw.text((500, 88), "登记日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 145), "夫妻姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 145), "李四", font=self.text_font, fill='black')
        draw.text((50, 195), "女方身份证：110105199501015678", font=self.text_font, fill='black')
        draw.text((50, 245), "男方身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 295), "婚姻状况：已婚", font=self.text_font, fill='black')
        draw.text((400, 295), "生育登记类型：一孩登记", font=self.text_font, fill='black')
        draw.text((50, 345), "孕育情况：已怀孕", font=self.text_font, fill='black')
        draw.text((400, 345), "预产期：2026-10-15", font=self.text_font, fill='black')
        draw.text((50, 395), "居住地址：北京市朝阳区建国路88号", font=self.text_font, fill='black')
        draw.text((50, 445), "所属街道：朝阳区建外街道", font=self.text_font, fill='black')
        draw.text((50, 495), "登记状态：已登记", font=self.title_font, fill='green')
        draw.text((400, 495), "发证日期：2026-03-30", font=self.text_font, fill='black')
        draw.rectangle([50, 550, 750, 610], fill='#ddd')
        draw.text((150, 555), "朝阳区卫生健康委员会", font=self.text_font, fill='#c01c28')
        draw.text((150, 590), "生育登记专用章", font=self.small_font, fill='#c01c28')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    # ========== 身后类测试数据 ==========

    def create_will_notary(self, filename="01_遗嘱公证书.png"):
        """遗嘱公证书"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((250, 10), "遗嘱公证书", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 200, 280], fill='#ddd')
        draw.text((80, 160), "公证处", font=self.text_font, fill='#666')
        draw.text((250, 90), "立遗嘱人：张三", font=self.text_font, fill='black')
        draw.text((500, 90), "编号：YZ202603300001", font=self.text_font, fill='black')
        draw.text((250, 140), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((250, 190), "遗嘱内容：房产由子女继承", font=self.text_font, fill='black')
        draw.text((250, 240), "立遗嘱日期：2020-06-01", font=self.text_font, fill='black')
        draw.text((250, 290), "公证日期：2020-06-15", font=self.text_font, fill='black')
        draw.text((250, 340), "公证员：李公证", font=self.text_font, fill='black')
        draw.text((250, 390), "公证处：北京市公证处", font=self.text_font, fill='black')
        draw.text((250, 440), "状态：有效", font=self.title_font, fill='green')
        draw.rectangle([50, 500, 750, 550], fill='#ddd')
        draw.text((150, 520), "公证专用章", font=self.text_font, fill='#666')
        img.save(self.output_dir / 'test_data' / filename)
        return img

    def create_bequest_agreement(self, filename="02_遗赠协议.png"):
        """遗赠协议"""
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((250, 10), "遗赠协议", font=self.title_font, fill='white')
        draw.text((50, 80), "遗赠人：张三", font=self.text_font, fill='black')
        draw.text((400, 80), "协议编号：YZXY20260330001", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 180), "受遗赠人：李四", font=self.text_font, fill='black')
        draw.text((50, 230), "身份证：110105199501015678", font=self.text_font, fill='black')
        draw.text((50, 280), "遗赠内容：存款50万元", font=self.text_font, fill='black')
        draw.text((50, 330), "签订日期：2024-01-15", font=self.text_font, fill='black')
        draw.text((50, 380), "见证人：王五", font=self.text_font, fill='black')
        draw.text((50, 430), "协议状态：生效", font=self.title_font, fill='green')
        draw.rectangle([50, 480, 750, 530], fill='#ddd')
        draw.text((150, 500), "双方签字盖章", font=self.text_font, fill='#666')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_death_certificate_v2(self, filename="03_死亡医学证明.png"):
        """死亡医学证明"""
        img = Image.new('RGB', (800, 550), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#c01c28')
        draw.text((200, 10), "死亡医学证明书", font=self.title_font, fill='white')
        draw.text((50, 80), "死者姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 80), "编号：SW20260330001", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 180), "性别：男", font=self.text_font, fill='black')
        draw.text((400, 180), "年龄：36岁", font=self.text_font, fill='black')
        draw.text((50, 230), "死亡日期：2026-03-25", font=self.text_font, fill='black')
        draw.text((50, 280), "死亡地点：北京市人民医院", font=self.text_font, fill='black')
        draw.text((50, 330), "死亡原因：疾病", font=self.text_font, fill='black')
        draw.text((50, 380), "出具机构：北京市人民医院", font=self.text_font, fill='black')
        draw.text((50, 430), "证明日期：2026-03-25", font=self.text_font, fill='black')
        draw.text((50, 480), "医师签字：XXX", font=self.text_font, fill='black')
        img.save(self.output_dir / 'test_data' / filename)
        return img

    def create_cremation_certificate(self, filename="04_火化证明.png"):
        """火化证明"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#9141ac')
        draw.text((280, 10), "火化证明", font=self.title_font, fill='white')
        draw.text((50, 80), "逝者姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 80), "火化证号：HH20260330001", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 180), "死亡日期：2026-03-25", font=self.text_font, fill='black')
        draw.text((50, 230), "火化日期：2026-03-27", font=self.text_font, fill='black')
        draw.text((50, 280), "火化机构：北京市八宝山殡仪馆", font=self.text_font, fill='black')
        draw.text((50, 330), "骨灰存放：已领取", font=self.text_font, fill='black')
        draw.text((50, 380), "经办人：李四", font=self.text_font, fill='black')
        draw.rectangle([50, 430, 750, 480], fill='#ddd')
        draw.text((150, 445), "火化专用章", font=self.text_font, fill='#9141ac')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def create_self_written_will(self, filename="05_自书遗嘱.png"):
        """自书遗嘱"""
        img = Image.new('RGB', (800, 700), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((250, 10), "自书遗嘱", font=self.title_font, fill='white')
        draw.text((50, 80), "立遗嘱人：王五", font=self.text_font, fill='black')
        draw.text((400, 80), "日期：2023-05-20", font=self.text_font, fill='black')
        draw.text((50, 130), "身份证：110105199501015678", font=self.text_font, fill='black')
        draw.line([50, 170, 750, 170], fill='black', width=2)
        draw.text((50, 190), "本人自愿立此遗嘱，对本人财产作如下安排：", font=self.text_font, fill='black')
        draw.text((50, 240), "一、房产归配偶所有", font=self.text_font, fill='black')
        draw.text((50, 290), "二、存款均分给子女", font=self.text_font, fill='black')
        draw.text((50, 340), "三、其他财产按法定继承办理", font=self.text_font, fill='black')
        draw.line([50, 400, 750, 400], fill='black', width=2)
        draw.text((50, 420), "立遗嘱人签字：王五", font=self.text_font, fill='black')
        draw.text((50, 470), "见证人签字：张三", font=self.text_font, fill='black')
        draw.text((50, 520), "日期：2023-05-20", font=self.text_font, fill='black')
        img.save(self.output_dir / 'test_data' / filename)
        return filename

    def generate_pension_test_data(self):
        """生成养老模块的测试数据"""
        images = [
            self.create_pension_payment(),
            self.create_pension_payment_record(),
            self.create_pension_plan(),
            self.create_pension_insurance_card(),
            self.create_pension_bank_flow(),
            self.create_no_info_image(module_name="养老相关信息"),
        ]
        print(f"Generated {len(images)} pension test data images")
        return images

    def generate_ai_image(self, image_type: str, filename: str,
                          custom_params: dict = None) -> str:
        """使用AI生成逼真的测试数据图片（img2img方案）

        策略：
        1. 使用PIL渲染正确的文档层（含所有文字和结构）
        2. 将PIL文档作为img2img参考图传给AI，AI理解文档结构
        3. AI生成同结构但更真实的结果，中文文字完全正确

        Args:
            image_type: 图片类型，对应AI_IMAGE_PROMPTS中的键
            filename: 输出文件名
            custom_params: 自定义参数，用于填充提示词模板

        Returns:
            生成的文件名
        """
        if not self.use_ai:
            return None

        # 获取背景提示词（无文字的结构描述）
        bg_prompt = self.AI_IMAGE_PROMPTS.get(image_type + '_bg')
        full_prompt_template = self.AI_IMAGE_PROMPTS.get(image_type)

        # 创建AI生成器
        ai_generator = MultimodalImageGenerator(
            api_type=self.ai_api_type,
            api_key=self._ai_api_key
        )

        output_path = str(self.output_dir / 'test_data' / filename)

        # 方案A：有背景提示词 -> img2img（参考图=PIL文档）
        if bg_prompt:
            # 填充参数
            params = custom_params or {}
            params.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
            bg_prompt_filled = bg_prompt.format(**params)

            # 获取PIL完整文档（含所有文字和结构）
            pil_doc = self._create_pil_document(image_type, custom_params)

            # img2img：PIL文档作为参考图，AI生成同结构真实图片
            img = ai_generator.generate_image(
                prompt=bg_prompt_filled,
                output_path=output_path,
                fallback_image=pil_doc,
                reference_image=pil_doc
            )
        # 方案B：无背景提示词 -> 完整PIL图作为fallback
        elif full_prompt_template:
            params = custom_params or {}
            params.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
            full_prompt = full_prompt_template.format(**params)

            # 获取PIL备用图片
            fallback_img = self._create_pil_image(image_type)

            img = ai_generator.generate_image(
                prompt=full_prompt,
                output_path=output_path,
                fallback_image=fallback_img
            )
        else:
            print(f"Warning: No prompt found for image type: {image_type}")
            return None

        if img:
            return filename
        return None

    def _create_pil_document(self, image_type: str, custom_params: dict = None) -> Image:
        """根据类型创建PIL完整文档（用于与AI纹理叠加）

        返回完整RGB文档，包含所有文字和结构。
        与AI纹理Multiply叠加后，得到：文字清晰正确 + AI质感增强。

        Args:
            image_type: 图片类型
            custom_params: 自定义参数

        Returns:
            PIL Image (RGB, 完整文档)
        """
        if image_type == 'health_report':
            return self._create_doc_health_report(custom_params)
        elif image_type == 'job_registration':
            return self._create_doc_job_registration(custom_params)
        elif image_type == 'flight_ticket':
            return self._create_doc_flight_ticket(custom_params)
        elif image_type == 'map_screenshot':
            return self._create_doc_map_screenshot(custom_params)
        elif image_type == 'taxi_invoice':
            return self._create_doc_taxi_invoice(custom_params)
        elif image_type == 'travel_record':
            return self._create_doc_travel_record(custom_params)
        elif image_type == 'app_screenshot':
            return self._create_doc_app_screen(custom_params)
        elif image_type == 'supplementary':
            return self._create_doc_supplementary(custom_params)
        elif image_type == 'multiple_records':
            return self._create_doc_multiple_records(custom_params)
        elif image_type == 'warning_message':
            return self._create_doc_warning(custom_params)
        elif image_type == 'network_error':
            return self._create_doc_network_error(custom_params)
        elif image_type == 'cancel_operation':
            return self._create_doc_cancel(custom_params)
        elif image_type == 'no_info':
            return self._create_doc_landscape()
        elif image_type == 'train_ticket':
            return self._create_pil_train_ticket()
        elif image_type == 'flight_ticket':
            return self._create_pil_flight_ticket()
        elif image_type == 'taxi_invoice':
            return self._create_pil_taxi_invoice()
        elif image_type == 'marriage_certificate':
            return self._create_pil_marriage_certificate()
        else:
            return self._create_pil_no_info_image()

    # ============================================================
    # 完整文档绘制方法（RGB文档，与AI纹理Multiply叠加）
    # ============================================================

    def _create_doc_health_report(self, params: dict = None) -> Image:
        """健康体检报告 - 完整文档"""
        W, H = 800, 1100
        img = Image.new('RGB', (W, H), '#f8f9fa')  # 浅灰白背景
        draw = ImageDraw.Draw(img)

        try:
            hdr_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
            body_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
            red_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
        except:
            hdr_font = title_font = body_font = small_font = red_font = ImageFont.load_default()

        date_str = (params or {}).get('date', '2026-03-28')

        # 顶部蓝色标题栏
        draw.rectangle([40, 40, W - 40, 110], fill='#1a5fb4')
        draw.text((W // 2 - 100, 55), "健康体检报告", font=hdr_font, fill='white')

        # 副标题
        draw.rectangle([40, 115, W - 40, 145], fill='#dce8f5')
        draw.text((W // 2 - 120, 120), f"编号：JC{datetime.now().strftime('%Y%m%d')}001", font=small_font, fill='#1a5fb4')

        # 信息区块
        info_top = 165
        # 基本信息标题
        draw.rectangle([40, info_top, 160, info_top + 32], fill='#e8f0fe')
        draw.text((50, info_top + 5), "基本信息", font=body_font, fill='#1a5fb4')
        draw.line([40, info_top + 36, W - 40, info_top + 36], fill='#c0d0e8', width=1)

        # 基本信息行
        row_y = info_top + 48
        draw.text((60, row_y), "姓    名：", font=body_font, fill='#333')
        draw.text((170, row_y), "张三", font=body_font, fill='#111')
        draw.text((360, row_y), "性    别：", font=body_font, fill='#333')
        draw.text((470, row_y), "男", font=body_font, fill='#111')

        row_y += 40
        draw.text((60, row_y), "证件号码：", font=body_font, fill='#333')
        draw.text((170, row_y), "110105199001011234", font=body_font, fill='#111')
        draw.text((360, row_y), "出生日期：", font=body_font, fill='#333')
        draw.draw.text((470, row_y), "1990-01-01", font=body_font, fill='#111') if False else None
        draw.text((470, row_y), "1990-01-01", font=body_font, fill='#111')

        row_y += 40
        draw.text((60, row_y), "体检日期：", font=body_font, fill='#333')
        draw.text((170, row_y), date_str, font=body_font, fill='#111')
        draw.text((360, row_y), "体检医院：", font=body_font, fill='#333')
        draw.text((470, row_y), "北京市人民医院", font=body_font, fill='#111')

        # 体检结果标题
        result_top = info_top + 160
        draw.rectangle([40, result_top, 160, result_top + 32], fill='#e8f0fe')
        draw.text((50, result_top + 5), "体检结果", font=body_font, fill='#1a5fb4')
        draw.line([40, result_top + 36, W - 40, result_top + 36], fill='#c0d0e8', width=1)

        # 结果：合格标签
        draw.rounded_rectangle([60, result_top + 50, 180, result_top + 100], radius=8, fill='#26a269')
        draw.text((85, result_top + 62), "合格", font=title_font, fill='white')

        # 体检项目表格
        table_top = result_top + 130
        # 表头
        draw.rectangle([40, table_top, W - 40, table_top + 36], fill='#e8f0fe')
        headers = [("检查项目", 60), ("结果", 300), ("参考值", 500)]
        for txt, x in headers:
            draw.text((x, table_top + 8), txt, font=body_font, fill='#1a5fb4')

        items = [
            ("身高体重", "175cm / 70kg", "正常范围"),
            ("血    压", "120/80 mmHg", "90-140/60-90"),
            ("视    力", "左1.5 右1.5", "≥0.5"),
            ("心电图", "正常", "正常"),
            ("血    常", "正常", "正常"),
        ]
        for i, (name, val, ref) in enumerate(items):
            row = table_top + 40 + i * 38
            bg = '#f0f4f8' if i % 2 == 0 else 'white'
            draw.rectangle([40, row, W - 40, row + 34], fill=bg)
            draw.text((60, row + 6), name, font=small_font, fill='#333')
            draw.text((300, row + 6), val, font=small_font, fill='#111')
            draw.text((500, row + 6), ref, font=small_font, fill='#666')
            draw.line([40, row + 34, W - 40, row + 34], fill='#e0e8f0', width=1)

        # 医生签名区
        sig_y = table_top + 240
        draw.line([40, sig_y, W - 40, sig_y], fill='#c0d0e8', width=1)
        draw.text((60, sig_y + 15), "医生签名：", font=body_font, fill='#333')
        draw.ellipse([200, sig_y + 8, 270, sig_y + 55], fill='#c01c28')  # 印章
        draw.text((208, sig_y + 20), "医院", font=red_font, fill='white')
        draw.text((280, sig_y + 15), "主任医师：李医生", font=body_font, fill='#111')

        # 底部说明
        draw.rectangle([40, H - 80, W - 40, H - 45], fill='#f0f4f8')
        draw.text((60, H - 73), f"本报告仅作为健康参考，不作为法律凭证。如有疑问请在3个工作日内联系体检医院。", font=small_font, fill='#666')

        # 边框
        draw.rectangle([40, 40, W - 40, H - 40], outline='#c0d0e8', width=2)
        return img

    def _create_doc_job_registration(self, params: dict = None) -> Image:
        """求职登记表 - 完整文档"""
        W, H = 800, 1100
        img = Image.new('RGB', (W, H), '#fffef5')  # 米白纸张色
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 顶部标题
        draw.rectangle([40, 40, W - 40, 105], fill='#9141ac')
        draw.text((W // 2 - 90, 52), "求职登记表", font=hdr, fill='white')

        # 副标题
        draw.rectangle([40, 110, W - 40, 140], fill='#f3e8ff')
        draw.text((60, 118), f"表单编号：JOB{datetime.now().strftime('%Y%m%d')}001    登记日期：{datetime.now().strftime('%Y-%m-%d')}", font=small, fill='#9141ac')

        y = 160
        # 基本信息区块
        draw.rectangle([40, y, 200, y + 32], fill='#f3e8ff')
        draw.text((55, y + 5), "基本信息", font=title, fill='#9141ac')
        draw.line([40, y + 36, W - 40, y + 36], fill='#d0b8f0', width=1)

        fields = [
            ("姓    名", "李四", 60, y + 48),
            ("性    别", "男", 60, y + 88),
            ("联系电话", "13800138000", 60, y + 128),
            ("电子邮箱", "lisi@example.com", 60, y + 168),
            ("求职意向", "软件工程师", 60, y + 208),
            ("期望薪资", "20000元/月", 60, y + 248),
            ("工作年限", "5年", 60, y + 288),
            ("学    历", "本科", 60, y + 328),
        ]

        for label, value, x, row_y in fields:
            draw.text((x, row_y), label + "：", font=body, fill='#555')
            draw.text((x + 120, row_y), value, font=body, fill='#111')

        # 教育背景
        edu_y = y + 380
        draw.rectangle([40, edu_y, 200, edu_y + 32], fill='#f3e8ff')
        draw.text((55, edu_y + 5), "教育背景", font=title, fill='#9141ac')
        draw.line([40, edu_y + 36, W - 40, edu_y + 36], fill='#d0b8f0', width=1)
        draw.text((60, edu_y + 50), "2010-09 至 2014-07    北京大学    计算机科学与技术    本科", font=small, fill='#333')

        # 工作经历
        exp_y = edu_y + 100
        draw.rectangle([40, exp_y, 200, exp_y + 32], fill='#f3e8ff')
        draw.text((55, exp_y + 5), "工作经历", font=title, fill='#9141ac')
        draw.line([40, exp_y + 36, W - 40, exp_y + 36], fill='#d0b8f0', width=1)
        draw.text((60, exp_y + 50), "2014-08 至 2019-12    某科技公司    Java开发工程师", font=small, fill='#333')
        draw.text((60, exp_y + 78), "2019-12 至今          某互联网公司    技术经理", font=small, fill='#333')

        # 红色印章
        draw.ellipse([580, edu_y + 50, 710, edu_y + 150], fill='#c01c28')
        draw.text((600, edu_y + 80), "人才", font=title, fill='white')
        draw.text((620, edu_y + 115), "中心", font=title, fill='white')

        # 边框
        draw.rectangle([40, 40, W - 40, H - 40], outline='#d0b8f0', width=2)
        return img

    def _create_doc_flight_ticket(self, params: dict = None) -> Image:
        """电子客票行程单 - 完整文档"""
        W, H = 800, 600
        img = Image.new('RGB', (W, H), '#f0fff4')  # 浅绿背景
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
            big = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
        except:
            hdr = title = body = small = big = ImageFont.load_default()

        date_str = (params or {}).get('date', '2026-03-28')

        # 顶部绿色标题
        draw.rectangle([0, 0, W, 70], fill='#1e7b34')
        draw.text((30, 15), "中国东方航空", font=hdr, fill='white')
        draw.text((580, 15), "ELECTRONIC TICKET", font=small, fill='#c8e6c9')
        draw.text((30, 48), "电子客票行程单/行程证明", font=small, fill='#c8e6c9')

        # 航班信息主区域
        draw.rectangle([30, 85, W - 30, 200], fill='white', outline='#1e7b34', width=2)

        # 左侧：出发信息
        draw.text((60, 100), "出发", font=small, fill='#1e7b34')
        draw.text((60, 125), "PEK", font=big, fill='#111')
        draw.text((60, 175), "北京首都机场 T3", font=body, fill='#555')

        # 中间：航班详情
        mid_x = W // 2 - 80
        draw.text((mid_x, 100), "航班号", font=small, fill='#666')
        draw.text((mid_x, 125), "MU5137", font=title, fill='#1e7b34')
        draw.text((mid_x, 165), "14:30 - 16:45", font=body, fill='#333')
        draw.text((mid_x, 195), "飞行时长：2小时15分", font=small, fill='#888')

        # 箭头
        draw.polygon([(290, 145), (310, 135), (310, 155)], fill='#1e7b34')

        # 右侧：到达信息
        draw.text((600, 100), "到达", font=small, fill='#1e7b34')
        draw.text((600, 125), "SHA", font=big, fill='#111')
        draw.text((600, 175), "上海虹桥机场 T2", font=body, fill='#555')

        # 旅客信息
        draw.rectangle([30, 215, W - 30, 260], fill='#f8f8f8', outline='#ddd', width=1)
        draw.text((60, 225), "旅客姓名：", font=body, fill='#555')
        draw.text((170, 225), "王五", font=body, fill='#111')
        draw.text((350, 225), "舱位：", font=body, fill='#555')
        draw.text((430, 225), "经济舱", font=body, fill='#111')
        draw.text((580, 225), "座位：", font=body, fill='#555')
        draw.text((660, 225), "23K", font=body, fill='#111')

        # 票务信息
        draw.rectangle([30, 270, W - 30, 350], fill='white', outline='#ddd', width=1)
        draw.text((60, 285), "票号：781-1234567890", font=small, fill='#666')
        draw.text((400, 285), "机票价格", font=small, fill='#666')
        draw.text((400, 310), "¥880.00", font=title, fill='#c01c28')
        draw.text((400, 340), "含税", font=small, fill='#888')

        # 底部条码区域
        draw.rectangle([30, 360, W - 30, 420], fill='#f5f5f5')
        # 条形码示意
        for i in range(80):
            x = 60 + i * 8
            h = 40 if i % 3 != 0 else 30
            draw.rectangle([x, 390 - h, x + 4, 390], fill='black')

        draw.text((60, 435), f"旅行日期：{date_str}    签注：OK    承运人：中国东方航空", font=small, fill='#666')

        return img

    def _create_doc_taxi_invoice(self, params: dict = None) -> Image:
        """出租车发票 - 完整文档"""
        W, H = 580, 900
        img = Image.new('RGB', (W, H), '#ffffff')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
            big = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 32)
        except:
            hdr = title = body = big = ImageFont.load_default()

        date_str = (params or {}).get('date', '2026-03-28')

        # 顶部
        draw.rectangle([0, 0, W, 60], fill='#1a1a1a')
        draw.text((W // 2 - 60, 12), "出租车发票", font=hdr, fill='white')

        # 发票代码区
        draw.rectangle([20, 75, W - 20, 115], fill='#f5f5f5', outline='#ddd', width=1)
        draw.text((30, 82), f"发票代码：111001600111    发票号码：12345678", font=body, fill='#333')

        # 行程信息
        draw.line([20, 125, W - 20, 125], fill='#ddd', width=1)
        draw.text((30, 135), "出租车号", font=title, fill='#666')
        draw.text((30, 165), "京BQ8888", font=hdr, fill='#111')

        draw.text((300, 135), "司机", font=title, fill='#666')
        draw.text((300, 165), "张师傅", font=hdr, fill='#111')

        # 分隔线
        draw.line([20, 205, W - 20, 205], fill='#ddd', width=1)

        # 上下车时间
        draw.text((30, 215), "上车时间", font=title, fill='#666')
        draw.text((30, 245), f"{date_str}", font=body, fill='#111')
        draw.text((200, 245), "09:15", font=body, fill='#111')

        draw.text((30, 285), "下车时间", font=title, fill='#666')
        draw.text((30, 315), "09:45", font=body, fill='#111')

        # 分隔线
        draw.line([20, 355, W - 20, 355], fill='#ddd', width=1)

        # 里程和等候
        draw.text((30, 365), "里程", font=title, fill='#666')
        draw.text((30, 395), "8.2公里", font=body, fill='#111')

        draw.text((200, 365), "等候时间", font=title, fill='#666')
        draw.text((200, 395), "5分钟", font=body, fill='#111')

        draw.text((330, 365), "单价", font=title, fill='#666')
        draw.text((330, 395), "3.00元/公里", font=body, fill='#111')

        # 金额（醒目）
        draw.rectangle([20, 430, W - 20, 510], fill='#fff3e0')
        draw.text((30, 438), "金额", font=title, fill='#c01c28')
        draw.text((30, 465), "¥68.50", font=big, fill='#c01c28')

        # 印章
        draw.ellipse([380, 440, 500, 500], fill='#c01c28')
        draw.text((395, 455), "发票", font=title, fill='white')
        draw.text((395, 485), "专用", font=title, fill='white')

        # 二维码区域
        draw.rectangle([20, 530, W - 20, 700], fill='#f5f5f5')
        # 二维码方格
        for row in range(12):
            for col in range(12):
                if (row + col) % 3 == 0:
                    x = 80 + col * 35
                    y = 545 + row * 12
                    draw.rectangle([x, y, x + 30, y + 10], fill='black')

        draw.text((30, 720), f"此发票由出租车公司开具，仅限报销使用", font=body, fill='#999')
        draw.text((30, 750), f"开票时间：{date_str} 09:45", font=body, fill='#999')

        # 边框
        draw.rectangle([10, 10, W - 10, H - 10], outline='#ddd', width=2)
        return img

    def _create_doc_map_screenshot(self, params: dict = None) -> Image:
        """导航截图 - 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#1a2a3a')  # 深蓝色（导航背景）
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 模拟地图方格
        for row in range(20):
            for col in range(14):
                shade = 30 + ((row + col) % 2) * 15
                draw.rectangle([col * 57, 100 + row * 55, (col + 1) * 57, 100 + (row + 1) * 55], fill=(shade, shade + 10, shade + 20))

        # 路线（橙色线条）
        points = [(0, 600), (100, 550), (200, 480), (300, 400), (400, 350), (500, 320), (600, 300), (800, 280)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill='#ff6b00', width=12)

        # 起点标记
        draw.ellipse([30, 570, 90, 630], fill='#26a269')
        draw.text((42, 580), "A", font=body, fill='white')

        # 终点标记
        draw.ellipse([740, 240, 800, 300], fill='#c01c28')
        draw.text((752, 250), "B", font=body, fill='white')

        # 底部信息面板
        draw.rectangle([0, H - 350, W, H], fill='white')
        draw.rectangle([0, H - 350, W, H - 345], fill='#e0e0e0', width=3)

        draw.text((40, H - 330), "北京市内导航", font=small, fill='#666')
        draw.text((40, H - 280), "北京故宫博物院", font=title, fill='#111')
        draw.text((40, H - 235), "北京161医院分院", font=title, fill='#111')

        # 分隔线
        draw.line([40, H - 195, W - 40, H - 195], fill='#e0e0e0', width=1)

        # 行程信息
        draw.text((40, H - 180), "行程距离", font=small, fill='#666')
        draw.text((40, H - 150), "8.5公里", font=hdr, fill='#1a5fb4')

        draw.text((300, H - 180), "预计时间", font=small, fill='#666')
        draw.text((300, H - 150), "约25分钟", font=hdr, fill='#1a5fb4')

        draw.text((580, H - 180), "预计费用", font=small, fill='#666')
        draw.text((580, H - 150), "约35元", font=hdr, fill='#1a5fb4')

        # 导航按钮
        draw.rounded_rectangle([40, H - 110, W - 40, H - 50], radius=12, fill='#1a5fb4')
        draw.text((W // 2 - 60, H - 97), "开始导航", font=title, fill='white')

        return img

    def _create_doc_travel_record(self, params: dict = None) -> Image:
        """出行记录汇总 - 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#f5f7fa')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
            big = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 30)
        except:
            hdr = title = body = small = big = ImageFont.load_default()

        date_str = (params or {}).get('date', '2026-03-28')

        # 顶部
        draw.rectangle([0, 0, W, 100], fill='#1a5fb4')
        draw.text((40, 25), "出勤记录", font=hdr, fill='white')
        draw.text((500, 30), date_str, font=body, fill='#c8e0f8')

        # 统计卡片
        card_y = 120
        cards = [("出行次数", "5", '#e8f0fe'), ("合计费用", "¥1012.5", '#fff3e0'), ("记录时间", "全天", '#f0fff4')]
        card_w = (W - 80) // 3
        for i, (label, val, color) in enumerate(cards):
            x = 40 + i * (card_w + 10)
            draw.rounded_rectangle([x, card_y, x + card_w, card_y + 100], radius=12, fill=color, outline='#ddd', width=1)
            draw.text((x + 20, card_y + 15), label, font=small, fill='#666')
            draw.text((x + 20, card_y + 50), val, font=big, fill='#111')

        # 记录列表
        list_y = 250
        draw.rectangle([40, list_y, W - 40, list_y + 50], fill='#e8f0fe')
        draw.text((60, list_y + 12), "类型", font=body, fill='#1a5fb4')
        draw.text((250, list_y + 12), "日期", font=body, fill='#1a5fb4')
        draw.text((450, list_y + 12), "金额", font=body, fill='#1a5fb4')
        draw.text((600, list_y + 12), "备注", font=body, fill='#1a5fb4')

        records = [
            ("地铁", "3月1日", "¥6.0", "上班通勤", '#e8f5e9'),
            ("地铁", "3月2日", "¥6.0", "上班通勤", '#e8f5e9'),
            ("打车", "3月5日", "¥45.0", "外出办事", '#fff3e0'),
            ("火车票", "3月10日", "¥553.0", "出差北京", '#e3f2fd'),
            ("机票", "3月15日", "¥880.0", "出差上海", '#e3f2fd'),
            ("自驾", "3月20日", "¥30.0", "停车费", '#fce4ec'),
        ]

        for i, (typ, date, amt, note, color) in enumerate(records):
            row = list_y + 55 + i * 70
            draw.rectangle([40, row, W - 40, row + 62], fill=color if i % 2 == 0 else 'white', outline='#eee', width=1)
            draw.text((60, row + 18), typ, font=body, fill='#333')
            draw.text((250, row + 18), date, font=body, fill='#333')
            draw.text((450, row + 18), amt, font=body, fill='#c01c28')
            draw.text((600, row + 18), note, font=small, fill='#888')

        return img

    def _create_doc_app_screen(self, params: dict = None) -> Image:
        """APP截图（补充信息）- 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#f0f2f5')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 手机状态栏
        draw.rectangle([0, 0, W, 50], fill='#1a1a1a')
        draw.text((40, 15), "9:41", font=body, fill='white')
        draw.rectangle([W - 60, 12, W - 40, 28], outline='white', width=2)  # 信号
        draw.rectangle([W - 35, 12, W - 20, 28], outline='white', width=2)  # 电池

        # 顶部导航
        draw.rectangle([0, 50, W, 130], fill='#1a5fb4')
        draw.text((W // 2 - 60, 65), "出勤记录", font=hdr, fill='white')

        # 内容卡片
        card_y = 160
        draw.rounded_rectangle([30, card_y, W - 30, card_y + 300], radius=16, fill='white', outline='#ddd', width=1)
        draw.rectangle([30, card_y, W - 30, card_y + 50], fill='#e8f0fe', outline='#ddd', width=1)
        draw.rounded_rectangle([30, card_y + 4, 100, card_y + 46], radius=6, fill='#26a269')
        draw.text((50, card_y + 14), "✓", font=title, fill='white')
        draw.text((115, card_y + 12), "已识别到出勤记录", font=title, fill='#111')

        draw.text((60, card_y + 75), "出勤记录信息已识别完成，可以补充更多信息：", font=body, fill='#555')

        # 补充项目
        items = [("收据/发票", "上传相关收据或发票"), ("照片", "补充相关场景照片"), ("文档", "上传其他证明材料")]
        for i, (name, desc) in enumerate(items):
            row = card_y + 115 + i * 55
            draw.ellipse([60, row + 5, 85, row + 30], fill='#e8f0fe', outline='#1a5fb4', width=2)
            draw.text((65, row + 8), "○", font=body, fill='#1a5fb4')
            draw.text((100, row), name, font=body, fill='#333')
            draw.text((100, row + 28), desc, font=small, fill='#888')

        # 底部按钮
        draw.rounded_rectangle([30, card_y + 250, W // 2 - 20, card_y + 295], radius=12, fill='#f0f2f5', outline='#ddd', width=1)
        draw.text((70, card_y + 263), "补充信息", font=body, fill='#333')

        draw.rounded_rectangle([W // 2 + 20, card_y + 250, W - 30, card_y + 295], radius=12, fill='#1a5fb4')
        draw.text((W // 2 + 55, card_y + 263), "自动记录", font=body, fill='white')

        return img

    def _create_doc_multiple_records(self, params: dict = None) -> Image:
        """多条出行记录列表 - 完整文档"""
        return self._create_doc_travel_record(params)

    def _create_doc_supplementary(self, params: dict = None) -> Image:
        """补充信息界面 - 完整文档"""
        return self._create_doc_app_screen(params)

    def _create_doc_warning(self, params: dict = None) -> Image:
        """警告提示界面 - 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#f5f5f5')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 手机状态栏
        draw.rectangle([0, 0, W, 50], fill='#1a1a1a')
        draw.text((40, 15), "9:41", font=body, fill='white')

        # 顶部
        draw.rectangle([0, 50, W, 130], fill='#c01c28')
        draw.text((W // 2 - 60, 65), "出勤记录", font=hdr, fill='white')

        # 警告对话框
        cx, cy = W // 2, H // 2 - 100
        draw.rounded_rectangle([cx - 300, cy - 150, cx + 300, cy + 200], radius=20, fill='white', outline='#c01c28', width=3)

        # 警告图标
        draw.ellipse([cx - 35, cy - 130, cx + 35, cy - 60], fill='#c01c28')
        draw.text((cx - 8, cy - 125), "!", font=hdr, fill='white')

        draw.text((cx - 80, cy - 50), "内容不合规", font=title, fill='#c01c28')
        draw.text((cx - 260, cy + 5), "您上传的图片/内容可能包含不适合", font=body, fill='#333')
        draw.text((cx - 260, cy + 35), "公开发布的信息（如暴力、不当信息等）", font=body, fill='#333')
        draw.text((cx - 260, cy + 65), "建议调整后发布", font=body, fill='#555')
        draw.line([cx - 260, cy + 95, cx + 260, cy + 95], fill='#eee', width=1)
        draw.text((cx - 260, cy + 108), "当次内容将不会为您记录", font=small, fill='#c01c28')

        # 按钮
        draw.rounded_rectangle([cx - 120, cy + 150, cx + 120, cy + 200], radius=12, fill='#1a5fb4')
        draw.text((cx - 35, cy + 163), "我知道了", font=body, fill='white')

        return img

    def _create_doc_network_error(self, params: dict = None) -> Image:
        """网络异常界面 - 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#f0f2f5')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 手机状态栏
        draw.rectangle([0, 0, W, 50], fill='#1a1a1a')
        draw.text((40, 15), "9:41", font=body, fill='white')

        # 顶部
        draw.rectangle([0, 50, W, 130], fill='#666')
        draw.text((W // 2 - 60, 65), "出勤记录", font=hdr, fill='white')

        # 错误图标（断开云）
        cx, cy = W // 2, H // 2 - 150
        draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill='#e0e0e0')
        draw.text((cx - 50, cy - 60), "☁", font=hdr, fill='#999')  # 云朵
        draw.line([cx - 50, cy + 30, cx + 50, cy + 30], fill='#e0e0e0', width=8)  # 断开线

        draw.text((cx - 80, cy + 100), "网络连接不佳", font=title, fill='#333')
        draw.text((cx - 100, cy + 140), "日志上传失败", font=body, fill='#666')
        draw.text((cx - 160, cy + 180), "请检查网络连接，尝试切换Wi-Fi或移动数据", font=small, fill='#999')

        # 重试按钮
        draw.rounded_rectangle([cx - 100, cy + 230, cx + 100, cy + 285], radius=12, fill='#1a5fb4')
        draw.text((cx - 35, cy + 248), "[重试]", font=title, fill='white')

        return img

    def _create_doc_cancel(self, params: dict = None) -> Image:
        """取消操作界面 - 完整文档"""
        W, H = 800, 1200
        img = Image.new('RGB', (W, H), '#f0f2f5')
        draw = ImageDraw.Draw(img)

        try:
            hdr = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 36)
            title = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
            body = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
            small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        except:
            hdr = title = body = small = ImageFont.load_default()

        # 手机状态栏
        draw.rectangle([0, 0, W, 50], fill='#1a1a1a')
        draw.text((40, 15), "9:41", font=body, fill='white')

        # 顶部
        draw.rectangle([0, 50, W, 130], fill='#888')
        draw.text((W // 2 - 60, 65), "出勤记录", font=hdr, fill='white')

        cx, cy = W // 2, H // 2 - 100
        draw.rounded_rectangle([cx - 300, cy - 120, cx + 300, cy + 150], radius=20, fill='white', outline='#ddd', width=2)

        # 对勾图标
        draw.ellipse([cx - 40, cy - 100, cx + 40, cy - 20], fill='#e8f5e9', outline='#26a269', width=2)
        draw.text((cx - 12, cy - 90), "✓", font=title, fill='#26a269')

        draw.text((cx - 60, cy + 10), "操作已取消", font=title, fill='#555')
        draw.text((cx - 160, cy + 55), "您已取消当前操作", font=body, fill='#666')
        draw.text((cx - 200, cy + 90), "若您还有其他需求，欢迎随时向我咨询", font=small, fill='#999')

        return img

    def _create_doc_landscape(self) -> Image:
        """风景图片（no_info类型）- 纯白色作为占位"""
        W, H = 1024, 768
        img = Image.new('RGB', (W, H), '#e8f5e9')
        draw = ImageDraw.Draw(img)
        # 简单蓝天白云背景
        draw.rectangle([0, 0, W, H // 2], fill='#87ceeb')  # 天空
        draw.rectangle([0, H // 2, W, H], fill='#228b22')  # 草地
        return img

    # ============================================================
    # PIL图片fallback（用于无AI提示词时的备用）
    # ============================================================
    def _create_pil_image(self, image_type: str) -> Image:
        """根据类型创建PIL图片（用于无AI提示词时的fallback）"""
        if image_type == 'train_ticket':
            return self._create_pil_train_ticket()
        elif image_type == 'flight_ticket':
            return self._create_pil_flight_ticket()
        elif image_type == 'taxi_invoice':
            return self._create_pil_taxi_invoice()
        elif image_type == 'marriage_certificate':
            return self._create_pil_marriage_certificate()
        elif image_type == 'no_info':
            return self._create_pil_no_info_image()
        elif image_type == 'health_report':
            return self._create_pil_health_report()
        elif image_type == 'job_registration':
            return self._create_pil_job_registration()
        elif image_type == 'map_screenshot':
            return self._create_pil_map_screenshot()
        elif image_type == 'app_screenshot':
            return self._create_pil_app_screenshot()
        elif image_type == 'network_error':
            return self._create_pil_network_error()
        elif image_type == 'cancel_operation':
            return self._create_pil_cancel_operation()
        elif image_type == 'warning_message':
            return self._create_pil_warning_message()
        elif image_type == 'multiple_records':
            return self._create_pil_multiple_records()
        elif image_type == 'supplementary':
            return self._create_pil_supplementary()
        elif image_type == 'will_notary':
            return self.create_will_notary()
        elif image_type == 'death_certificate':
            return self.create_death_certificate_v2()
        elif image_type == 'pension_record':
            return self.create_pension_payment()
        elif image_type == 'id_card':
            return self.create_id_card()
        elif image_type == 'business_license':
            return self.create_business_license()
        elif image_type == 'data_asset_report':
            return self.create_data_asset_report()
        elif image_type == 'data_asset_certificate':
            return self.create_data_asset_certificate()
        elif image_type == 'notary_certificate':
            return self.create_notary_certificate()
        else:
            return self._create_pil_no_info_image()

    def _create_text_overlay(self, image_type: str, custom_params: dict = None) -> Image:
        """创建透明背景的PIL文字层，用于叠加到AI背景图上

        返回RGBA图片，只有文字区域是不透明的，其他区域完全透明。
        这样合成时可以完美叠加：AI视觉背景 + PIL正确汉字。
        """
        # 各类型统一尺寸
        W, H = 1024, 768
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        params = custom_params or {}
        date_str = params.get('date', datetime.now().strftime('%Y-%m-%d'))

        if image_type == 'health_report':
            # 体检报告文字层
            self._overlay_health_report(draw, W, H, params, date_str)
        elif image_type == 'job_registration':
            self._overlay_job_registration(draw, W, H, params)
        elif image_type == 'flight_ticket':
            self._overlay_flight_ticket(draw, W, H, params, date_str)
        elif image_type == 'map_screenshot':
            self._overlay_map_screenshot(draw, W, H, params)
        elif image_type == 'taxi_invoice':
            self._overlay_taxi_invoice(draw, W, H, params, date_str)
        elif image_type == 'travel_record':
            self._overlay_travel_record(draw, W, H, params, date_str)
        elif image_type == 'app_screenshot':
            self._overlay_app_screenshot(draw, W, H, params)
        elif image_type == 'network_error':
            self._overlay_network_error(draw, W, H)
        elif image_type == 'cancel_operation':
            self._overlay_cancel_operation(draw, W, H)
        elif image_type == 'warning_message':
            self._overlay_warning_message(draw, W, H)
        elif image_type == 'multiple_records':
            self._overlay_multiple_records(draw, W, H, params, date_str)
        elif image_type == 'supplementary':
            self._overlay_supplementary(draw, W, H)
        elif image_type == 'train_ticket':
            self._overlay_train_ticket(draw, W, H, params, date_str)

        return img

    def _overlay_train_ticket(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """火车票文字层"""
        # 标题栏背景
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 50, 70, "火车票", 36, 'white')

        # 主信息
        self._draw_text(draw, 80, 160, "G1234  高铁", 32, (192, 28, 40, 255))
        self._draw_text(draw, 80, 220, f"出发站：北京南", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 270, f"到达站：上海虹桥", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 320, f"日期：{date_str}  08:30", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 370, f"票价：553.00元", 26, (0, 0, 0, 255))
        self._draw_text(draw, 550, 160, "二等座  08车  12A号", 26, (0, 0, 0, 255))
        self._draw_text(draw, 550, 220, "乘客姓名：张三", 26, (0, 0, 0, 255))

    def _overlay_health_report(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """体检报告文字层"""
        # 标题栏
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "健康体检报告", 36, 'white')

        # 主信息
        self._draw_text(draw, 80, 160, "姓名：张三", 28, (0, 0, 0, 255))
        self._draw_text(draw, 350, 160, f"体检日期：{date_str}", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "体检医院：北京市人民医院", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 260, "体检结果：合格", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 310, "身高：175cm    体重：70kg    血压：正常    视力：正常", 26, (0, 0, 0, 255))

        # 印章区域
        draw.ellipse([700, 400, 880, 580], fill=(200, 50, 50, 180))
        self._draw_text(draw, 730, 455, "医院", 28, (255, 255, 255, 255))
        self._draw_text(draw, 730, 495, "公章", 28, (255, 255, 255, 255))

    def _overlay_job_registration(self, draw: ImageDraw.Draw, W: int, H: int, params: dict):
        """求职登记表文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "求职登记表", 36, 'white')

        self._draw_text(draw, 80, 160, "姓名：李四", 28, (0, 0, 0, 255))
        self._draw_text(draw, 350, 160, "联系电话：13800138000", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "求职意向：软件工程师", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 260, "期望薪资：20000元/月", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 310, "工作经验：5年    学历：本科", 26, (0, 0, 0, 255))

        draw.ellipse([700, 400, 880, 580], fill=(200, 50, 50, 180))
        self._draw_text(draw, 730, 465, "公章", 28, (255, 255, 255, 255))

    def _overlay_flight_ticket(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """机票文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(38, 120, 56, 230))
        self._draw_text(draw, W // 2 - 80, 70, "电子客票行程单", 36, 'white')

        self._draw_text(draw, 80, 160, "航班号：MU5137  中国东方航空", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "出发：PEK 北京首都机场 T3", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 260, "到达：SHA 上海虹桥机场 T2", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 310, f"日期：{date_str}  时间：14:30 - 16:45", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 360, "乘客：王五    舱位：经济舱    座位：23K", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 400, "票价：880.00元（含税）", 26, (0, 0, 0, 255))

    def _overlay_map_screenshot(self, draw: ImageDraw.Draw, W: int, H: int, params: dict):
        """导航截图文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "导航行程", 36, 'white')

        self._draw_text(draw, 80, 160, "起点：北京故宫博物院", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "终点：北京161医院分院", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 260, "行程距离：8.5公里", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 300, "预估时间：约25分钟", 28, (0, 0, 0, 255))

    def _overlay_taxi_invoice(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """打车发票文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 60, 70, "出租车发票", 36, 'white')

        self._draw_text(draw, 80, 160, f"发票代码：111001600111", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 200, f"发票号码：12345678", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 240, f"出租车号：京BQ8888", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 280, f"上车：{date_str}  09:15", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 315, f"下车：09:45", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 350, f"里程：8.2公里    等候：5分钟", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 390, f"金额：68.50元", 32, (0, 0, 0, 255))

    def _overlay_travel_record(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """出行记录汇总文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "出行记录汇总", 36, 'white')

        self._draw_text(draw, 80, 160, f"{date_str} 出行记录：", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "地铁出行：2次  合计：12元", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 250, "打车出行：1次  68.5元", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 290, "步行记录：8000步", 26, (0, 0, 0, 255))

    def _overlay_app_screenshot(self, draw: ImageDraw.Draw, W: int, H: int, params: dict):
        """APP截图文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "APP界面", 36, 'white')

        self._draw_text(draw, 80, 160, "已识别到必要的出勤记录信息", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "您还可以补充相关信息：", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 250, "收据、发票或照片作为证明", 26, (0, 0, 0, 255))

    def _overlay_network_error(self, draw: ImageDraw.Draw, W: int, H: int):
        """网络异常文字层"""
        draw.rectangle([200, 200, W - 200, H - 200], fill=(220, 220, 220, 240))
        self._draw_text(draw, W // 2 - 100, 240, "网络连接不佳", 32, (150, 0, 0, 255))
        self._draw_text(draw, W // 2 - 150, 300, "日志上传失败", 28, (0, 0, 0, 255))
        self._draw_text(draw, W // 2 - 180, 350, "请检查网络连接，尝试切换Wi-Fi", 26, (100, 100, 100, 255))
        self._draw_text(draw, W // 2 - 60, 390, "[重试]", 28, (26, 95, 180, 255))

    def _overlay_cancel_operation(self, draw: ImageDraw.Draw, W: int, H: int):
        """取消操作文字层"""
        draw.rectangle([200, 200, W - 200, H - 200], fill=(240, 240, 240, 240))
        self._draw_text(draw, W // 2 - 100, 240, "操作已取消", 32, (100, 100, 100, 255))
        self._draw_text(draw, W // 2 - 150, 300, "您已取消当前操作", 28, (0, 0, 0, 255))
        self._draw_text(draw, W // 2 - 180, 350, "若您还有其他需求，欢迎随时向我咨询", 24, (100, 100, 100, 255))

    def _overlay_warning_message(self, draw: ImageDraw.Draw, W: int, H: int):
        """警告提示文字层"""
        draw.rectangle([150, 180, W - 150, H - 180], fill=(255, 230, 230, 250))
        self._draw_text(draw, W // 2 - 100, 210, "内容不合规", 36, (192, 28, 40, 255))
        self._draw_text(draw, W // 2 - 220, 270, "您上传的图片/内容可能包含不适合公开发布的信息", 24, (0, 0, 0, 255))
        self._draw_text(draw, W // 2 - 180, 310, "建议调整后发布，当次内容将不会为您记录", 24, (0, 0, 0, 255))

    def _overlay_multiple_records(self, draw: ImageDraw.Draw, W: int, H: int, params: dict, date_str: str):
        """多条出行记录文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "出行记录列表", 36, 'white')

        self._draw_text(draw, 80, 160, f"{date_str[:7]}月出行记录汇总：", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "3月1日  地铁  6元", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 250, "3月5日  打车  45元", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 290, "3月10日  火车票  553元  出发08:30 到达12:45", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 330, "3月15日  机票  880元  出发14:30 到达16:45", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 370, "3月20日  自驾停车  30元", 26, (0, 0, 0, 255))

    def _overlay_supplementary(self, draw: ImageDraw.Draw, W: int, H: int):
        """补充信息文字层"""
        draw.rectangle([60, 60, W - 60, 120], fill=(26, 95, 180, 230))
        self._draw_text(draw, W // 2 - 80, 70, "补充信息", 36, 'white')

        self._draw_text(draw, 80, 160, "已识别到必要的出勤记录信息", 28, (0, 0, 0, 255))
        self._draw_text(draw, 80, 210, "您还可以补充相关信息：", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 250, "收据、发票或照片作为证明", 26, (0, 0, 0, 255))
        self._draw_text(draw, 80, 300, '如果没有补充内容，可以选择"自动记录"', 26, (0, 0, 0, 255))

    def _draw_text(self, draw: ImageDraw.Draw, x: int, y: int, text: str, size: int, color):
        """在指定位置绘制文字，使用微软雅黑字体"""
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", size)
        except:
            font = ImageFont.load_default()
        draw.text((x, y), text, font=font, fill=color)

    def _create_pil_health_report(self) -> Image:
        """PIL: 健康体检报告"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((370, 75), "健康体检报告", font=self.title_font, fill='white')
        draw.text((80, 170), "姓名：张三", font=self.text_font, fill='black')
        draw.text((550, 170), "体检日期：2026-03-28", font=self.text_font, fill='black')
        draw.text((80, 230), "体检医院：北京市人民医院", font=self.text_font, fill='black')
        draw.text((80, 290), "体检结果：合格", font=self.text_font, fill='black')
        draw.text((80, 350), "身高：175cm  体重：70kg  血压：正常  视力：正常", font=self.small_font, fill='black')
        draw.ellipse([700, 420, 870, 590], fill='#c01c28')
        draw.text((745, 470), "医院", font=self.text_font, fill='white')
        draw.text((755, 510), "公章", font=self.text_font, fill='white')
        return img

    def _create_pil_job_registration(self) -> Image:
        """PIL: 求职登记表"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((390, 75), "求职登记表", font=self.title_font, fill='white')
        draw.text((80, 170), "姓名：李四", font=self.text_font, fill='black')
        draw.text((550, 170), "联系电话：13800138000", font=self.text_font, fill='black')
        draw.text((80, 230), "求职意向：软件工程师", font=self.text_font, fill='black')
        draw.text((80, 290), "期望薪资：20000元/月", font=self.text_font, fill='black')
        draw.text((80, 350), "工作经验：5年  学历：本科", font=self.small_font, fill='black')
        draw.ellipse([700, 420, 870, 590], fill='#c01c28')
        draw.text((755, 480), "公章", font=self.text_font, fill='white')
        return img

    def _create_pil_map_screenshot(self) -> Image:
        """PIL: 导航截图"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((430, 75), "导航行程", font=self.title_font, fill='white')
        draw.text((80, 170), "起点：北京故宫博物院", font=self.text_font, fill='black')
        draw.text((80, 230), "终点：北京161医院分院", font=self.text_font, fill='black')
        draw.text((80, 290), "行程距离：8.5公里", font=self.text_font, fill='black')
        draw.text((80, 340), "预估时间：约25分钟", font=self.text_font, fill='black')
        return img

    def _create_pil_taxi_invoice(self) -> Image:
        """PIL: 打车发票"""
        img = Image.new('RGB', (800, 500), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((280, 10), "出租车发票", font=self.title_font, fill='white')
        draw.text((50, 80), "发票代码：111001600111", font=self.text_font, fill='black')
        draw.text((50, 130), "发票号码：12345678", font=self.text_font, fill='black')
        draw.text((50, 180), "出租车号：京BQ8888", font=self.text_font, fill='black')
        draw.text((50, 230), "上车：2026-03-28  09:15", font=self.text_font, fill='black')
        draw.text((50, 275), "下车：09:45", font=self.text_font, fill='black')
        draw.text((50, 320), "里程：8.2公里  等候：5分钟", font=self.text_font, fill='black')
        draw.text((50, 370), "金额：68.50元", font=self.title_font, fill='#c01c28')
        return img

    def _create_pil_app_screenshot(self) -> Image:
        """PIL: APP截图（补充信息）"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((400, 75), "APP界面", font=self.title_font, fill='white')
        draw.text((80, 160), "已识别到必要的出勤记录信息", font=self.text_font, fill='black')
        draw.text((80, 220), "您还可以补充相关信息：", font=self.text_font, fill='black')
        draw.text((80, 280), "收据、发票或照片作为证明", font=self.text_font, fill='black')
        return img

    def _create_pil_network_error(self) -> Image:
        """PIL: 网络异常"""
        img = Image.new('RGB', (1024, 768), 'lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([200, 200, 824, 568], fill='white')
        draw.text((360, 250), "网络连接不佳", font=self.title_font, fill='#c01c28')
        draw.text((360, 320), "日志上传失败", font=self.text_font, fill='black')
        draw.text((280, 380), "请检查网络连接，尝试切换Wi-Fi", font=self.text_font, fill='gray')
        draw.rectangle([400, 440, 624, 490], fill='#1a5fb4')
        draw.text((460, 452), "重试", font=self.text_font, fill='white')
        return img

    def _create_pil_cancel_operation(self) -> Image:
        """PIL: 取消操作"""
        img = Image.new('RGB', (1024, 768), 'lightgray')
        draw = ImageDraw.Draw(img)
        draw.rectangle([200, 200, 824, 568], fill='white')
        draw.text((400, 250), "操作已取消", font=self.title_font, fill='gray')
        draw.text((360, 320), "您已取消当前操作", font=self.text_font, fill='black')
        draw.text((280, 380), "若您还有其他需求，欢迎随时向我咨询", font=self.text_font, fill='gray')
        return img

    def _create_pil_warning_message(self) -> Image:
        """PIL: 警告提示"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([150, 180, 874, 588], fill='#fff0f0', outline='#c01c28', width=3)
        draw.text((390, 210), "内容不合规", font=self.title_font, fill='#c01c28')
        draw.text((200, 280), "您上传的图片/内容可能包含不适合公开发布的信息", font=self.text_font, fill='black')
        draw.text((200, 340), "建议调整后发布，当次内容将不会为您记录", font=self.text_font, fill='black')
        return img

    def _create_pil_multiple_records(self) -> Image:
        """PIL: 多条出行记录"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((390, 75), "出行记录列表", font=self.title_font, fill='white')
        draw.text((80, 160), "2026年3月出行记录汇总：", font=self.text_font, fill='black')
        draw.text((80, 220), "3月1日   地铁    6元", font=self.text_font, fill='black')
        draw.text((80, 265), "3月5日   打车    45元", font=self.text_font, fill='black')
        draw.text((80, 310), "3月10日  火车票  553元    出发08:30 到达12:45", font=self.text_font, fill='black')
        draw.text((80, 355), "3月15日  机票    880元    出发14:30 到达16:45", font=self.text_font, fill='black')
        draw.text((80, 400), "3月20日  自驾停车  30元", font=self.text_font, fill='black')
        return img

    def _create_pil_supplementary(self) -> Image:
        """PIL: 补充信息"""
        img = Image.new('RGB', (1024, 768), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([60, 60, 964, 130], fill='#1a5fb4')
        draw.text((400, 75), "补充信息", font=self.title_font, fill='white')
        draw.text((80, 160), "已识别到必要的出勤记录信息", font=self.text_font, fill='black')
        draw.text((80, 220), "您还可以补充相关信息：", font=self.text_font, fill='black')
        draw.text((80, 280), "收据、发票或照片作为证明", font=self.text_font, fill='black')
        draw.text((80, 340), '如果没有补充内容，可以选择"自动记录"', font=self.text_font, fill='black')
        return img

    def _create_pil_train_ticket(self) -> Image:
        """PIL备用：火车票"""
        img = Image.new('RGB', (800, 450), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#1a5fb4')
        draw.text((250, 10), "火车票", font=self.title_font, fill='white')
        draw.text((50, 80), "G1234", font=self.title_font, fill='#c01c28')
        draw.text((400, 80), "2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 140), "出发站：北京南", font=self.text_font, fill='black')
        draw.text((50, 185), "到达站：上海虹桥", font=self.text_font, fill='black')
        draw.text((50, 230), "出发时间：08:30", font=self.text_font, fill='black')
        draw.text((50, 275), "到达时间：12:45", font=self.text_font, fill='black')
        draw.text((50, 320), "票价：553.00元", font=self.text_font, fill='black')
        draw.text((50, 365), "乘客：张三", font=self.text_font, fill='black')
        draw.text((500, 140), "座位：二等座", font=self.text_font, fill='black')
        draw.text((500, 185), "车厢：08车", font=self.text_font, fill='black')
        draw.text((500, 230), "座位号：12A", font=self.text_font, fill='black')
        return img

    def _create_pil_flight_ticket(self) -> Image:
        """PIL备用：机票"""
        img = Image.new('RGB', (800, 550), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 60], fill='#26a269')
        draw.text((300, 10), "电子客票", font=self.title_font, fill='white')
        draw.text((200, 90), "MU5137", font=self.title_font, fill='#1a5fb4')
        draw.text((400, 90), "中国东方航空", font=self.text_font, fill='black')
        draw.text((200, 150), "出发：PEK 北京首都 T3", font=self.text_font, fill='black')
        draw.text((200, 200), "到达：SHA 上海虹桥 T2", font=self.text_font, fill='black')
        draw.text((200, 250), "日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((200, 300), "出发时间：14:30", font=self.text_font, fill='black')
        draw.text((400, 300), "到达时间：16:45", font=self.text_font, fill='black')
        draw.text((500, 150), "乘客：李四", font=self.text_font, fill='black')
        draw.text((500, 200), "座位：23K 经济舱", font=self.text_font, fill='black')
        return img

    def _create_pil_taxi_invoice(self) -> Image:
        """PIL备用：打车发票"""
        img = Image.new('RGB', (600, 400), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 600, 50], fill='#1a5fb4')
        draw.text((200, 10), "出租车发票", font=self.title_font, fill='white')
        draw.text((50, 80), "车号：京BQ8888", font=self.text_font, fill='black')
        draw.text((50, 130), "上车：2026-03-30 09:15", font=self.text_font, fill='black')
        draw.text((50, 180), "下车：2026-03-30 09:45", font=self.text_font, fill='black')
        draw.text((50, 230), "里程：12.5公里", font=self.text_font, fill='black')
        draw.text((50, 280), "金额：48.00元", font=self.title_font, fill='green')
        return img

    def _create_pil_marriage_certificate(self) -> Image:
        """PIL备用：结婚证"""
        img = Image.new('RGB', (1000, 750), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 1000, 65], fill='#c01c28')
        draw.text((390, 12), "结婚证", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 230, 290], fill='#ddd')
        draw.text((115, 165), "照片", font=self.text_font, fill='#666')
        draw.rectangle([270, 80, 450, 290], fill='#ddd')
        draw.text((335, 165), "照片", font=self.text_font, fill='#666')
        # 夫方信息
        draw.text((50, 305), "夫：张三", font=self.text_font, fill='black')
        draw.text((50, 345), "出生日期：1990-01-01", font=self.text_font, fill='black')
        draw.text((50, 385), "民族：汉族", font=self.text_font, fill='black')
        draw.text((50, 425), "户籍所在地：北京市朝阳区", font=self.text_font, fill='black')
        draw.text((50, 465), "身份证：110105199001011234", font=self.text_font, fill='black')
        # 妻方信息
        draw.text((520, 305), "妻：李四", font=self.text_font, fill='black')
        draw.text((520, 345), "出生日期：1995-05-15", font=self.text_font, fill='black')
        draw.text((520, 385), "民族：汉族", font=self.text_font, fill='black')
        draw.text((520, 425), "户籍所在地：上海市浦东新区", font=self.text_font, fill='black')
        draw.text((520, 465), "身份证：110105199501015678", font=self.text_font, fill='black')
        # 共同信息
        draw.text((50, 515), "登记日期：2020-05-20", font=self.text_font, fill='black')
        draw.text((520, 515), "登记机关：北京市民政局", font=self.text_font, fill='black')
        draw.text((50, 555), "结婚证号：J202005200001", font=self.text_font, fill='black')
        draw.rectangle([50, 600, 950, 640], fill='#ddd')
        draw.text((245, 605), "中华人民共和国婚姻登记专用章", font=self.text_font, fill='#c01c28')
        return img

    def _create_pil_hukou_book(self) -> Image:
        """PIL备用：户口本"""
        img = Image.new('RGB', (700, 950), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 700, 60], fill='#1a5fb4')
        draw.text((220, 10), "中华人民共和国", font=self.title_font, fill='white')
        draw.text((250, 50), "户口簿", font=self.title_font, fill='white')
        draw.rectangle([50, 90, 650, 130], fill='#ddd')
        draw.text((80, 95), "户号：110105001001", font=self.text_font, fill='black')
        draw.text((420, 95), "户主：张三", font=self.text_font, fill='black')
        draw.rectangle([50, 140, 650, 175], fill='#1a5fb4')
        draw.text((60, 142), "姓名", font=self.small_font, fill='white')
        draw.text((160, 142), "关系", font=self.small_font, fill='white')
        draw.text((250, 142), "出生日期", font=self.small_font, fill='white')
        draw.text((370, 142), "身份证", font=self.small_font, fill='white')
        draw.text((530, 142), "民族", font=self.small_font, fill='white')
        draw.rectangle([50, 175, 650, 210], fill='#f8f8f8')
        draw.text((70, 178), "张三", font=self.small_font, fill='black')
        draw.text((165, 178), "户主", font=self.small_font, fill='black')
        draw.text((260, 178), "1990-01-01", font=self.small_font, fill='black')
        draw.text((340, 178), "110105199001011234", font=self.small_font, fill='black')
        draw.text((545, 178), "汉族", font=self.small_font, fill='black')
        draw.rectangle([50, 210, 650, 245], fill='white')
        draw.text((70, 213), "李四", font=self.small_font, fill='black')
        draw.text((165, 213), "配偶", font=self.small_font, fill='black')
        draw.text((260, 213), "1995-05-15", font=self.small_font, fill='black')
        draw.text((340, 213), "110105199501015678", font=self.small_font, fill='black')
        draw.text((545, 213), "汉族", font=self.small_font, fill='black')
        draw.rectangle([50, 245, 650, 280], fill='#f8f8f8')
        draw.text((70, 248), "张小一", font=self.small_font, fill='black')
        draw.text((165, 248), "子女", font=self.small_font, fill='black')
        draw.text((260, 248), "2026-01-15", font=self.small_font, fill='black')
        draw.text((340, 248), "110105202601150010", font=self.small_font, fill='black')
        draw.text((545, 248), "汉族", font=self.small_font, fill='black')
        draw.rectangle([50, 290, 650, 350], fill='white')
        draw.text((60, 298), "住址：北京市朝阳区建国路88号1号楼101室", font=self.text_font, fill='black')
        draw.text((60, 333), "本户人数：3人", font=self.text_font, fill='black')
        draw.rectangle([50, 360, 650, 395], fill='#ddd')
        draw.text((60, 365), "发证日期：2020-05-20    登记机关：北京市公安局朝阳分局", font=self.small_font, fill='black')
        draw.rectangle([50, 405, 650, 440], fill='#1a5fb4')
        draw.text((60, 408), "变更记录", font=self.small_font, fill='white')
        draw.rectangle([50, 440, 650, 475], fill='#f8f8f8')
        draw.text((60, 443), "2020-05-20    新立户", font=self.small_font, fill='black')
        draw.rectangle([50, 475, 650, 510], fill='white')
        draw.text((60, 478), "2026-01-15    子女出生登记（张小一）", font=self.small_font, fill='black')
        draw.rectangle([50, 510, 650, 545], fill='#f8f8f8')
        draw.text((60, 513), "2026-03-30    婚姻状况变更（李四迁入）", font=self.small_font, fill='black')
        draw.rectangle([50, 870, 650, 920], fill='#ddd')
        draw.text((180, 875), "北京市公安局朝阳分局户口专用章", font=self.text_font, fill='#c01c28')
        return img

    def _create_pil_settlement_certificate(self) -> Image:
        """PIL备用：落户证明"""
        img = Image.new('RGB', (800, 700), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 65], fill='#1a5fb4')
        draw.text((250, 10), "落户证明", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 750, 130], fill='#f0f4ff')
        draw.text((60, 88), "编号：LH202603300001", font=self.text_font, fill='black')
        draw.text((500, 88), "日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 145), "申请人姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 145), "身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 195), "原户籍地：北京市朝阳区", font=self.text_font, fill='black')
        draw.text((400, 195), "联系电话：13800138000", font=self.text_font, fill='black')
        draw.text((50, 245), "落户地址：北京市海淀区中关村大街1号", font=self.text_font, fill='black')
        draw.text((400, 245), "户籍性质：城镇户口", font=self.text_font, fill='black')
        draw.text((50, 295), "落户类型：人才引进", font=self.text_font, fill='black')
        draw.text((400, 295), "申请日期：2026-03-15", font=self.text_font, fill='black')
        draw.text((50, 345), "审批状态：已通过", font=self.title_font, fill='green')
        draw.text((400, 345), "审批日期：2026-03-25", font=self.text_font, fill='black')
        draw.text((50, 395), "审批机关：北京市海淀区公安分局", font=self.text_font, fill='black')
        draw.text((50, 445), "承办人：刘警官", font=self.text_font, fill='black')
        draw.rectangle([50, 500, 750, 660], fill='#ddd')
        draw.text((150, 505), "北京市海淀区公安分局", font=self.text_font, fill='#c01c28')
        draw.text((150, 545), "落户审批专用章", font=self.small_font, fill='#c01c28')
        return img

    def _create_pil_fertility_registration(self) -> Image:
        """PIL备用：生育登记"""
        img = Image.new('RGB', (800, 650), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 800, 65], fill='#26a269')
        draw.text((250, 10), "生育登记服务单", font=self.title_font, fill='white')
        draw.rectangle([50, 80, 750, 130], fill='#f0f8f0')
        draw.text((60, 88), "登记编号：SY202603300001", font=self.text_font, fill='black')
        draw.text((500, 88), "登记日期：2026-03-30", font=self.text_font, fill='black')
        draw.text((50, 145), "夫妻姓名：张三", font=self.text_font, fill='black')
        draw.text((400, 145), "李四", font=self.text_font, fill='black')
        draw.text((50, 195), "女方身份证：110105199501015678", font=self.text_font, fill='black')
        draw.text((50, 245), "男方身份证：110105199001011234", font=self.text_font, fill='black')
        draw.text((50, 295), "婚姻状况：已婚", font=self.text_font, fill='black')
        draw.text((400, 295), "生育登记类型：一孩登记", font=self.text_font, fill='black')
        draw.text((50, 345), "孕育情况：已怀孕", font=self.text_font, fill='black')
        draw.text((400, 345), "预产期：2026-10-15", font=self.text_font, fill='black')
        draw.text((50, 395), "居住地址：北京市朝阳区建国路88号", font=self.text_font, fill='black')
        draw.text((50, 445), "所属街道：朝阳区建外街道", font=self.text_font, fill='black')
        draw.text((50, 495), "登记状态：已登记", font=self.title_font, fill='green')
        draw.text((400, 495), "发证日期：2026-03-30", font=self.text_font, fill='black')
        draw.rectangle([50, 550, 750, 610], fill='#ddd')
        draw.text((150, 555), "朝阳区卫生健康委员会", font=self.text_font, fill='#c01c28')
        draw.text((150, 590), "生育登记专用章", font=self.small_font, fill='#c01c28')
        return img

    def _create_pil_no_info_image(self) -> Image:
        """PIL备用：不含有效信息图片"""
        img = Image.new('RGB', (600, 600), '#f0f0f0')
        draw = ImageDraw.Draw(img)
        draw.ellipse([150, 100, 450, 400], fill='#87CEEB')
        draw.text((220, 220), "风景", font=self.title_font, fill='white')
        draw.text((100, 450), "这是一张风景图片", font=self.text_font, fill='#666')
        draw.text((100, 500), "不包含证件或票据信息", font=self.text_font, fill='#666')
        return img

    def generate_all_test_data(self, use_ai: bool = None):
        """生成所有测试数据图片

        Args:
            use_ai: 是否使用AI生成，如果为None则使用实例的self.use_ai设置
        """
        use_ai = use_ai if use_ai is not None else self.use_ai
        self.use_ai = use_ai

        print(f"Generating test data images to: {self.output_dir / 'test_data'}")
        if use_ai:
            print("Using AI to generate realistic images...")
        else:
            print("Using PIL to generate simple images...")

        # 根据模块名自动选择生成方法
        module_lower = self.module_name.lower()
        if '时间轴' in module_lower or 'timeline' in module_lower:
            return self.generate_timeline_test_data()
        elif '婚育' in module_lower or 'marriage' in module_lower:
            return self.generate_marriage_test_data()
        elif '身后' in module_lower or 'behind' in module_lower:
            return self.generate_behind_test_data()
        elif '养老' in module_lower or 'pension' in module_lower:
            return self.generate_pension_test_data()
        elif '出勤' in module_lower or 'commute' in module_lower:
            return self.generate_commute_test_data()
        elif any(kw in module_lower for kw in ['公证', 'notary', '实名', '资产对接', '资质', '智能公证', '流程']):
            return self.generate_notary_test_data()
        else:
            # 默认出行类
            return self.generate_travel_test_data()

    def create_test_case_folders(self, positive_cases, negative_cases):
        """创建测试用例文件夹"""
        for i, (folder_name, screenshot_needed) in enumerate(positive_cases, 1):
            folder = self.output_dir / 'positive' / f"{self.module_name}_{folder_name}"
            folder.mkdir(parents=True, exist_ok=True)

        for i, (folder_name, screenshot_needed) in enumerate(negative_cases, len(positive_cases) + 1):
            folder = self.output_dir / 'negative' / f"{self.module_name}_{folder_name}"
            folder.mkdir(parents=True, exist_ok=True)

        print(f"Created test case folders")

    def generate_text_feature_doc(self, feature_name: str, feature_desc: str,
                                   positive_cases: list, negative_cases: list = None):
        """生成文本类AI功能的.md文档

        Args:
            feature_name: 功能名称（如：AI润色、AI扩写、AI缩写等）
            feature_desc: 功能描述
            positive_cases: 正向用例列表，每个用例包含(dict):
                - name: 用例名称
                - input: 输入描述
                - output: 预期输出描述
                - verify_points: 验证点列表
            negative_cases: 负向用例列表，格式同上
        """
        md_content = f"""# {self.module_name}_{feature_name}

## 功能描述

{feature_desc}

## 正向测试用例

"""
        for i, case in enumerate(positive_cases, 1):
            md_content += f"""### {self.module_name}_{i:02d}_{case['name']}

**测试类型**：正向

**输入**：
{case['input']}

**预期输出**：
{case['output']}

**验证点**：
"""
            for point in case.get('verify_points', []):
                md_content += f"- {point}\n"

        if negative_cases:
            md_content += """
## 负向测试用例

"""
            for i, case in enumerate(negative_cases, len(positive_cases) + 1):
                md_content += f"""### {self.module_name}_{i:02d}_{case['name']}

**测试类型**：负向

**输入**：
{case['input']}

**预期输出**：
{case['output']}

**验证点**：
"""
                for point in case.get('verify_points', []):
                    md_content += f"- {point}\n"

        md_content += """
## 测试数据

测试图片：`screenshot.png`

测试数据图片：`..\\..\\test_data\\`
"""
        return md_content

    def generate_all_text_feature_docs(self, features: list):
        """生成所有文本类功能的.md文档

        Args:
            features: 功能列表，每个包含:
                - name: 功能名称
                - desc: 功能描述
                - positive_cases: 正向用例
                - negative_cases: 负向用例（可选）
                - folder_name: 文件夹名称（可选，默认用序号）
        """
        for i, feature in enumerate(features, 1):
            md_content = self.generate_text_feature_doc(
                feature_name=feature['name'],
                feature_desc=feature['desc'],
                positive_cases=feature.get('positive_cases', []),
                negative_cases=feature.get('negative_cases')
            )

            # 保存到对应文件夹
            folder_name = feature.get('folder_name', f"{self.module_name}_{i:02d}_{feature['name']}")
            folder = self.output_dir / 'positive' / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            md_file = folder / f"{folder_name}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Generated: {md_file.name}")

    def print_structure(self):
        """打印目录结构"""
        print(f"\n{'='*60}")
        print(f"Output: {self.output_dir}")
        print(f"{'='*60}")

        for category in ['positive', 'negative']:
            path = self.output_dir / category
            if path.exists():
                label = "POSITIVE" if category == "positive" else "NEGATIVE"
                print(f"\n{label}:")
                for f in sorted(path.iterdir()):
                    if f.is_dir():
                        print(f"  /{f.name}/")

        test_data = self.output_dir / 'test_data'
        if test_data.exists():
            print(f"\nTEST DATA:")
            for f in sorted(test_data.iterdir()):
                if f.is_file():
                    print(f"  {f.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Axure原型测试用例生成',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  # 使用PIL生成简单测试图片
  python extract_prototype.py -u "https://xxx.com/出行.html" -m "出行"

  # 使用AI生成逼真测试图片
  python extract_prototype.py -u "https://xxx.com/出行.html" -m "出行" --ai-generate

  # 指定AI API类型
  python extract_prototype.py -u "https://xxx.com/婚育.html" -m "婚育" --ai-generate --ai-api claude
  python extract_prototype.py -u "https://xxx.com/婚育.html" -m "婚育" --ai-generate --ai-api openai

环境变量：
  CLAUDE_API_KEY / ANTHROPIC_API_KEY - Claude API密钥
  OPENAI_API_KEY - OpenAI API密钥
  DASHSCOPE_API_KEY - 通义千问API密钥
        """
    )
    parser.add_argument('--url', '-u', required=True, help='Axure原型页面URL')
    parser.add_argument('--module', '-m', help='模块名称（默认从URL提取）')
    parser.add_argument('--output', '-o', help='输出目录（默认当前目录/{模块名}testcases）')
    parser.add_argument('--no-screenshot', action='store_true', help='跳过截图生成')
    parser.add_argument('--type', '-t', choices=['travel', 'timeline', 'marriage', 'pension', 'behind', 'auto'],
                       default='auto', help='测试数据类型（默认auto自动检测）')
    parser.add_argument('--ai-generate', action='store_true',
                       help='使用多模态AI生成逼真的测试图片')
    parser.add_argument('--ai-api', choices=['claude', 'openai', 'qwen', 'zhipu'],
                       default='claude', help='AI API类型（默认claude）')

    args = parser.parse_args()

    print("=" * 60)
    print("  Axure原型测试用例生成")
    print("=" * 60)
    print(f"  URL: {args.url}")
    print(f"  Module: {args.module or 'auto'}")
    print(f"  Output: {args.output or 'auto'}")
    print(f"  Type: {args.type}")
    print(f"  AI Generate: {args.ai_generate}")
    if args.ai_generate:
        print(f"  AI API: {args.ai_api}")
    print("=" * 60)
    print()

    # 创建生成器
    generator = PrototypeTestCaseGenerator(
        url=args.url,
        module_name=args.module,
        output_dir=args.output,
        use_ai=args.ai_generate,
        ai_api_type=args.ai_api
    )

    # 生成测试数据
    generator.generate_all_test_data()

    # 打印结构
    generator.print_structure()

    print()
    print("=" * 60)
    print("  完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
