#!/usr/bin/env python3
"""
ZenTao TestCase Creator - 使用浏览器自动化创建测试用例
通过 Playwright 控制浏览器，模拟人工操作来创建包含完整步骤的测试用例
"""

import asyncio
import json
import sys
import requests
from playwright.async_api import async_playwright

# 配置
ZENDAO_URL = "http://192.168.0.28:9980"
ACCOUNT = "shidawei"
PASSWORD = "shidawei"
PRODUCT_ID = 1

# 测试用例数据
TEST_CASES = [
    {
        "title": "[P0] 林木基础信息录入-正常流程",
        "pri": "0",
        "story": 13,
        "steps": [
            ("进入【智能化优化版】页面", "页面正常加载，显示添加林木按钮"),
            ("点击添加林木按钮", "显示林木信息录入表单"),
            ("填写林木名称：海南黄花梨", "林木名称字段显示输入内容"),
            ("选择所在地区：四川省-成都市-金牛区", "省市区三级联动选择成功，显示完整地址"),
            ("选择地形地貌：山地", "地形地貌显示为山地"),
            ("点击确认按钮", "录入信息锁定，表单进入编辑状态"),
        ]
    },
    {
        "title": "[P0] 产权信息录入-正常流程",
        "pri": "0",
        "story": 13,
        "steps": [
            ("填写产权证编号：469007100024GE00004L00001234", "产权证编号字段显示正确"),
            ("点击权属期限输入框", "显示日期选择器"),
            ("选择开始日期：2012-12-21", "开始日期显示为2012-12-21"),
            ("选择结束日期：2062-12-21", "结束日期显示为2062-12-21"),
            ("填写占地面积：1.00㎡", "占地面积显示1.00㎡，单位正确"),
        ]
    },
    {
        "title": "[P0] 林木基本信息录入-正常流程",
        "pri": "0",
        "story": 13,
        "steps": [
            ("填写树高：18.0m", "树高字段显示18.0m，单位正确"),
            ("填写树龄：20年", "树龄字段显示20年"),
            ("填写胸径：10.0cm", "胸径字段显示10.0cm，单位正确"),
            ("提交表单", "基本信息完整保存，无校验错误"),
        ]
    },
    {
        "title": "[P1] 图片AI生成功能",
        "pri": "1",
        "story": 13,
        "steps": [
            ("进入林木图片上传区域", "显示手动上传和AI生成两个选项"),
            ("点击AI生成按钮", "显示『图片生成中...』状态提示"),
            ("等待AI生成完成（约5-10秒）", "生成完成后，按钮变为『重新生成』和『确认图片』"),
            ("对生成结果不满意，点击重新生成", "再次显示『图片生成中』，完成后显示新图片"),
            ("多次重新生成直到满意", "可反复重新生成，直到获得满意结果"),
            ("点击确认图片", "图片确认成功，林木图片区域显示已确认的图片"),
        ]
    },
    {
        "title": "[P1] 批量录入多条林木记录",
        "pri": "1",
        "story": 13,
        "steps": [
            ("点击批量录入按钮", "进入批量录入模式，界面切换为批量录入视图"),
            ("添加第一条林木记录（填写完整信息，上传图片）", "第一条记录添加成功，显示在列表中"),
            ("点击添加按钮新增第二条记录", "显示新的空白录入表单"),
            ("填写第二条林木记录（不同信息）", "第二条记录添加成功，与第一条记录独立"),
            ("检查两条记录是否各自独立（图片、产权证、详情图）", "每条记录包含各自独立的图片和证件信息，互不影响"),
            ("在批量模式下再次添加第三条记录", "可继续添加，记录数量无上限"),
        ]
    },
    {
        "title": "[P0] 必填字段校验-未填写时提示",
        "pri": "0",
        "story": 13,
        "steps": [
            ("进入页面，点击添加林木", "显示录入表单"),
            ("不填写任何必填字段，直接点击提交", "系统提示：『该字段为必填项』，高亮必填字段"),
            ("填写林木名称：测试林木", "林木名称字段验证通过，无错误提示"),
            ("不选择所在地区，直接提交", "系统提示：『所在地区为必填项』"),
            ("依次填写所有必填字段后提交", "所有必填字段验证通过，表单提交成功"),
        ]
    },
    {
        "title": "[P0] 产权人实名校验-不一致时提示",
        "pri": "0",
        "story": 13,
        "steps": [
            ("填写完整的产权信息（产权证编号、权属期限、占地面积）", "产权信息填写成功"),
            ("上传林木不动产权证", "不动产权证上传成功"),
            ("点击提交按钮", "系统开始校验产权人与实名信息"),
            ("产权人与当前登录用户实名信息不一致", "系统提示：『产权人与实名信息不一致，请重新上传』，阻止提交"),
            ("使用正确的产权人信息重新上传", "校验通过，表单提交成功"),
        ]
    },
    {
        "title": "[P1] 图片手动上传功能",
        "pri": "1",
        "story": 13,
        "steps": [
            ("进入林木图片上传区域", "显示手动上传和AI生成两个选项"),
            ("点击手动上传按钮", "打开文件选择对话框"),
            ("选择一张本地图片文件（支持jpg/png格式）", "文件名显示在界面上"),
            ("确认上传", "图片上传成功，显示缩略图"),
            ("再次点击上传按钮更换图片", "可成功更换图片"),
        ]
    },
    {
        "title": "[P1] 经纬度坐标录入",
        "pri": "1",
        "story": 13,
        "steps": [
            ("进入空间位置信息填写区域", "显示纬度坐标和经度坐标输入框"),
            ("通过高德地图搜索『东方市林业科学研究所』", "地图定位到该位置"),
            ("长按地图获取经纬度", "显示经纬度坐标"),
            ("将获取的坐标填入表单（纬度：19.X，经度：109.X）", "坐标显示正确"),
            ("手动修改坐标值测试格式校验", "格式错误时提示：『请输入有效的经纬度』"),
        ]
    },
]

async def login_and_create_cases():
    """登录禅道并创建测试用例"""
    created_ids = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. 登录禅道
            print("=== 1. 登录禅道 ===")
            await page.goto(f"{ZENDAO_URL}/index.php?m=user&f=login")
            await page.fill('input[name="account"]', ACCOUNT)
            await page.fill('input[name="password"]', PASSWORD)
            await page.click('button[type="submit"]')
            await page.wait_for_url("**/index.php**", timeout=10000)
            print("登录成功")
            
            # 2. 逐个创建测试用例
            for i, case in enumerate(TEST_CASES, 1):
                print(f"\n=== 创建用例 {i}/{len(TEST_CASES)}: {case['title']} ===")
                
                # 进入创建页面
                await page.goto(f"{ZENDAO_URL}/index.php?m=testcase&f=create&product={PRODUCT_ID}")
                await page.wait_for_load_state("networkidle")
                
                # 填写标题
                await page.fill('input[name="title"]', case['title'])
                
                # 选择优先级
                await page.select_option('select[name="pri"]', case['pri'])
                
                # 关联需求
                if case.get('story'):
                    # 点击需求选择框
                    await page.click('input[name="story"]')
                    await asyncio.sleep(0.5)
                    # 在弹出的列表中选择
                    await page.fill('input[name="story"]', str(case['story']))
                    await asyncio.sleep(0.5)
                
                # 添加步骤
                print(f"  添加 {len(case['steps'])} 个步骤...")
                
                for step_idx, (step_desc, step_expect) in enumerate(case['steps'], 1):
                    # 点击"添加步骤"按钮（第一个步骤需要点击添加，之后直接填写）
                    if step_idx == 1:
                        # 查找添加步骤按钮
                        add_btn = page.locator('button:has-text("添加步骤"), a:has-text("添加步骤"), .btn-add-step')
                        if await add_btn.count() > 0:
                            await add_btn.first.click()
                            await asyncio.sleep(0.3)
                    
                    # 填写步骤描述和预期
                    step_rows = page.locator('.steps-table tbody tr, .case-steps tr, #stepsTable tr')
                    row_count = await step_rows.count()
                    
                    if row_count >= step_idx:
                        row = step_rows.nth(step_idx - 1)
                        await row.locator('textarea[name*="steps"]').first.fill(step_desc)
                        # 预期结果可能在不同的输入框中
                        expect_inputs = row.locator('textarea[name*="expect"], input[name*="expect"]')
                        if await expect_inputs.count() > 0:
                            await expect_inputs.first.fill(step_expect)
                    
                    # 如果还有更多步骤，点击添加
                    if step_idx < len(case['steps']):
                        add_btn = page.locator('button:has-text("添加步骤"), a:has-text("添加步骤"), .btn-add-step')
                        if await add_btn.count() > 0:
                            await add_btn.first.click()
                            await asyncio.sleep(0.3)
                
                # 提交
                await page.click('button[type="submit"], .btn-submit, input[type="submit"]')
                await asyncio.sleep(1)
                
                # 获取创建后的 URL 或 ID
                current_url = page.url
                if 'id=' in current_url:
                    case_id = current_url.split('id=')[1].split('&')[0]
                    print(f"  创建成功！ID: {case_id}")
                    created_ids.append({'id': case_id, 'title': case['title']})
                else:
                    # 检查是否有错误提示
                    error_text = await page.locator('.alert, .message, .error').text_content()
                    if error_text:
                        print(f"  创建失败: {error_text[:100]}")
                    else:
                        print(f"  创建完成，当前URL: {current_url}")
                        created_ids.append({'title': case['title']})
            
            print(f"\n=== 完成！共创建 {len(created_ids)} 个用例 ===")
            for item in created_ids:
                print(f"  - {item}")
            
        except Exception as e:
            print(f"错误: {e}")
            # 截图调试
            await page.screenshot(path="/tmp/error_screenshot.png")
            print("截图已保存到 /tmp/error_screenshot.png")
        
        finally:
            await browser.close()
    
    return created_ids

if __name__ == "__main__":
    asyncio.run(login_and_create_cases())
