# 禅道Bug智能助手 Skill
# ZenTao Bug Assistant - OpenClaw Skill
# 包含: Bug查询、创建、IM通知

name: 禅道Bug智能助手
description: |
  使用AI快速查询禅道Bug和创建Bug，支持自动IM通知指派人。
  功能包括：
  - 查询禅道项目、迭代和Bug列表
  - 按项目/迭代查询Bug统计
  - 创建Bug（支持图片附件）
  - 自动通过OpenIM通知指派人
icon: "🐛"
icon_background: "#FFEAD5"
version: "1.0.0"
author: "石大卫"
tags:
  - 禅道
  - Bug管理
  - 质量管理
  - 自动化

# 环境配置
environment:
  zentao_url:
    description: "禅道服务地址"
    example: "http://192.168.0.28:9980"
    required: true

  zentao_account:
    description: "禅道登录账号"
    example: "shidawei"
    default: "shidawei"
    required: true

  zentao_password:
    description: "禅道登录密码"
    example: "shidawei"
    default: "shidawei"
    required: true

  openim_url:
    description: "OpenIM服务地址"
    example: "http://192.168.0.27:10002"
    required: false

  openim_token:
    description: "OpenIM访问Token"
    example: "eyJhbGciOiJIUzI1NiIs..."
    required: false

  default_project:
    description: "默认项目ID"
    example: "1"
    default: "1"
    required: false

  default_execution:
    description: "默认执行/迭代ID"
    example: "17"
    default: "17"
    required: false

# API端点模板
api_endpoints:
  get_token: "{zentao_url}/api.php/v1/tokens"
  get_programs: "{zentao_url}/api.php/v1/programs"
  get_projects: "{zentao_url}/api.php/v1/projects/{project_id}/executions"
  get_bugs: "{zentao_url}/api.php/v1/executions/{execution_id}/bugs"
  create_bug: "{zentao_url}/api.php/v1/products/1/bugs"
  get_users: "{zentao_url}/api.php/v1/users"

  openim_get_users: "{openim_url}/user/get_users"
  openim_send_msg: "{openim_url}/msg/send_msg"

# 核心工作流
workflow:
  # ============ 通用流程 ============
  step_1_login:
    name: "登录禅道获取Token"
    description: "使用账号密码登录禅道，获取API访问令牌"
    api:
      method: POST
      url: "{zentao_url}/api.php/v1/tokens"
      headers:
        Content-Type: "application/json"
      body:
        account: "{zentao_account}"
        password: "{zentao_password}"
    output:
      token: "从响应body中提取token字段"
      variable: "token"

  # ============ Bug查询流程 ============
  step_2_query_programs:
    name: "获取项目列表"
    description: "获取禅道中所有项目/产品列表"
    condition: "用户意图为查询Bug或项目信息"
    api:
      method: GET
      url: "{zentao_url}/api.php/v1/programs"
      headers:
        token: "{token}"
    output:
      programs: "项目列表JSON"

  step_3_extract_project_ids:
    name: "提取项目ID"
    description: "从项目列表中提取所有项目ID"
    llm:
      model: "deepseek-chat"
      instruction: "提取所有的项目ID，输出为数组格式"
    input:
      - "{programs}"
    output:
      project_ids: "项目ID数组"
      project_names: "项目名称数组（用于对照）"

  step_4_query_iterations:
    name: "批量获取迭代列表"
    description: "对每个项目ID并行查询其下的迭代/执行"
    iteration:
      parallel: true
      max_parallel: 4
      items: "{project_ids}"
    api:
      method: GET
      url: "{zentao_url}/api.php/v1/projects/id:{item}/executions"
      headers:
        token: "{token}"
      params:
        page: 1
        limit: 100
        status: "all"
    output:
      iterations: "各项目的迭代列表数组"

  step_5_extract_iteration_info:
    name: "提取迭代ID"
    description: "根据用户输入匹配正确的迭代"
    llm:
      model: "deepseek-chat"
      instruction: |
        根据用户的问题，提取对应的迭代ID。
        输入格式: {project_id: 1, id: [], project_name: "xxx", id_name: [[12,"迭代1"],[1,"迭代2"]]}
        如果用户提到具体迭代名，返回匹配的id数组；如果没有明确迭代，返回空数组。
    input:
      - "{iterations}"
      - "{project_ids}"
      - "{user_query}"
    output:
      matched_project_id: "匹配的项目ID"
      matched_iteration_ids: "匹配的迭代ID数组"

  step_6_query_bugs:
    name: "查询Bug列表"
    description: "查询指定迭代下的所有Bug"
    iteration:
      parallel: true
      max_parallel: 3
      items: "{matched_iteration_ids}"
    api:
      method: GET
      url: "{zentao_url}/api.php/v1/executions/{item}/bugs"
      headers:
        token: "{token}"
      params:
        page: 1
        limit: 200
        total: 200
    output:
      bugs: "Bug列表数组"

  step_7_analyze_bugs:
    name: "分析Bug统计"
    description: "使用LLM分析Bug数据，生成统计报告"
    llm:
      model: "deepseek-chat"
      instruction: |
        请按照以下步骤输出Bug情况：

        1. 首先分析提供的Bug数据，包括Bug编号、标题、状态、严重程度、优先级、创建时间、指派人和项目模块等信息

        2. 按照Bug状态进行分类统计，包括：未解决、待处理、处理中、待测试、已关闭、已拒绝等状态

        3. 按照严重程度统计Bug数量，包括：致命、严重、一般、轻微等级别

        4. 按照优先级统计Bug分布，包括：紧急、高、中、低等级别

        5. 识别出需要紧急关注的高优先级和高严重程度的Bug

        6. 统计每个模块或项目的Bug数量，找出问题集中的区域

        7. 统计Bug指派最多的开发

        8. 整理出关键数据点，包括：Bug总数、未解决Bug数、已解决Bug数、解决率等

        9. 用清晰简洁的语言描述当前Bug整体情况，突出重要问题和风险点

        10. 已解决的bug = 待验证的bug

        11. 未解决Bug高于10个都属于bug多的状态

        输出内容应该包含：
        - 总体概况（Bug总数、状态分布）
        - 按状态分类统计（激活状态、待测试状态、已解决状态）
        - 按严重程度和优先级的分类统计
        - 需要重点关注的问题
        - 主要风险和建议
        - 最后给出结论
    input:
      - "{bugs}"
    output:
      report: "Bug分析报告"

  # ============ Bug创建流程 ============
  step_8_extract_bug_info:
    name: "提取Bug信息"
    description: "从用户描述中提取Bug标题和指派人"
    llm:
      model: "deepseek-chat"
      instruction: |
        从用户描述中提取Bug信息：
        1. Bug标题 - 对Bug的描述作为标题
        2. 指派人 - 用户提到要修复问题的人（可选）
        3. 如果用户没有指定指派人，默认指派给"石大卫"
    input:
      - "{user_query}"
    output:
      bug_title: "Bug标题"
      bug_description: "Bug详细描述"
      assignee: "指派人名称（可选）"

  step_9_process_image:
    name: "处理图片附件"
    description: "如果用户提供了图片URL，转换为可访问的完整URL"
    code: |
      def main(image_url: str = None) -> dict:
          if image_url:
              base_url = "http://192.168.0.43:29012/"
              full_url = base_url.rstrip('/') + '/' + image_url.lstrip('/')
              return {'result': full_url}
          else:
              return {'result': ''}
    input:
      - "{user_image_url}"
    output:
      processed_image_url: "完整图片URL"

  step_10_get_zentao_users:
    name: "获取禅道用户列表"
    description: "获取禅道用户列表用于匹配指派人"
    api:
      method: GET
      url: "{zentao_url}/api.php/v1/users"
      headers:
        Token: "7dbadbc3b68b57aaa7a8db746d98235a"
      params:
        page: 1
        limit: 5000
    output:
      zentao_users: "用户列表JSON"

  step_11_match_assignee:
    name: "匹配指派人账号"
    description: "根据realname匹配account"
    code: |
      def main(user_list: str, target_name: str) -> dict:
          import json
          data = json.loads(user_list)
          target_account = ""
          for user in data.get("users", []):
              if user.get("realname") == target_name:
                  target_account = user.get("account", "")
                  break
          return {"result": target_account}
    input:
      - "{zentao_users}"
      - "{assignee}"
    output:
      assignee_account: "禅道账号"

  step_12_create_bug:
    name: "创建Bug"
    description: "在禅道中创建Bug"
    condition: "无指派人时使用默认指派"
    api:
      method: POST
      url: "{zentao_url}/api.php/v1/products/1/bugs"
      headers:
        token: "{token}"
        Content-Type: "application/json"
        User-Agent: "Apifox/1.0.0 (https://apifox.com)"
      body:
        title: "{bug_title}"
        severity: 2
        pri: 1
        project: "{default_project}"
        execution: "{default_execution}"
        type: "codeerror"
        openedBuild: ["trunk"]
        assignedTo: "{assignee}"
        steps: "禅道智能体 {bug_description} <a href={processed_image_url}>BUG图片</a>"
    output:
      bug_result: "创建结果"

  step_13_create_bug_with_assignee:
    name: "创建Bug(带指派人)"
    description: "创建Bug并指定指派人"
    condition: "有指派人时使用匹配到的账号"
    api:
      method: POST
      url: "{zentao_url}/api.php/v1/products/1/bugs"
      headers:
        token: "{token}"
        Content-Type: "application/json"
        User-Agent: "Apifox/1.0.0 (https://apifox.com)"
      body:
        title: "{bug_title}"
        severity: 2
        pri: 2
        project: "{default_project}"
        execution: "{default_execution}"
        type: "codeerror"
        openedBuild: ["trunk"]
        assignedTo: "{assignee_account}"
        steps: "禅道智能体 {bug_description} <a href={processed_image_url}>BUG图片</a>"
    output:
      bug_result: "创建结果"

  # ============ IM通知流程 ============
  step_14_get_openim_users:
    name: "获取IM用户列表"
    description: "从OpenIM获取用户列表"
    condition: "需要发送IM通知时"
    api:
      method: POST
      url: "{openim_url}/user/get_users"
      headers:
        token: "{openim_token}"
        Content-Type: "application/json"
      body:
        pagination:
          pageNumber: 1
          showNumber: 10000
    output:
      openim_users: "IM用户列表"

  step_15_get_user_id:
    name: "获取用户ID"
    description: "根据指派人姓名获取OpenIM用户ID"
    llm:
      model: "deepseek-chat"
      instruction: "{assignee} 提交指派人对应的user_id"
    input:
      - "{openim_users}"
    output:
      user_id: "OpenIM用户ID"

  step_16_generate_timestamp:
    name: "生成时间戳"
    description: "生成毫秒级时间戳"
    code: |
      def main() -> dict:
          import time
          timestamp = time.time()
          milliseconds_timestamp = int(timestamp * 1000)
          return {"result": milliseconds_timestamp}
    output:
      timestamp: "毫秒时间戳"

  step_17_send_im_notification:
    name: "发送IM通知"
    description: "通过OpenIM发送Bug创建通知给指派人"
    api:
      method: POST
      url: "{openim_url}/msg/send_msg"
      headers:
        token: "{openim_token}"
        Content-Type: "application/json"
        operationID: "1646445464564"
      body:
        sendID: "2"
        recvID: "{user_id}"
        groupID: ""
        senderNickname: "禅道智能助手"
        senderFaceURL: "http://www.head.com"
        senderPlatformID: 1
        content:
          content: "{bug_title} {assignee} {processed_image_url}"
        contentType: 101
        sessionType: 1
        isOnlineOnly: false
        notOfflinePush: false
        sendTime: "{timestamp}"
        offlinePushInfo:
          title: "BUG"
          desc: ""
          ex: ""
          iOSPushSound: "default"
          iOSBadgeCount: true
        ex: "ex"
    output:
      im_result: "发送结果"

# 问题分类规则
intent_classification:
  query_intents:
    - "查询禅道的Bug"
    - "查询迭代Bug情况"
    - "目前有哪些项目"
    - "Bug情况统计"
    - "项目迭代详情"
    - patterns:
        - "Bug情况"
        - "迭代*Bug"
        - "查询*Bug"

  create_intents:
    - "创建Bug"
    - "提交Bug"
    - "报告Bug"
    - "发现一个Bug"
    - "页面无法打开"
    - "功能不正常"
    - patterns:
        - "Bug"
        - "无法"
        - "不能"
        - "错误"

  unrelated_intents:
    - patterns:
        - "天气"
        - "新闻"
        - "娱乐"

# 响应模板
response_templates:
  query_success: |
    ## Bug查询结果

    {report}

    ---
    💡 如需查看具体Bug详情，请提供Bug编号或迭代名称。

  create_success: |
    ## ✅ Bug创建成功

    - **标题**: {bug_title}
    - **指派人**: {assignee}
    - **项目**: {default_project}
    - **执行**: {default_execution}

    {im_notification_status}

  create_failed: |
    ## ❌ Bug创建失败

    错误信息: {error}

    请重试或联系管理员。

  im_notification_sent: |
    ## 📱 IM通知已发送

    已通过OpenIM通知 **{assignee}**，请留意查收。

  im_notification_failed: |
    ## ⚠️ IM通知发送失败

    Bug已创建成功，但IM通知发送失败。

  no_matching_iteration: |
    ## ⚠️ 未找到匹配的迭代

    您输入的迭代信息在禅道中未找到。

    可选的迭代包括：
    {available_iterations}

    请输入准确的迭代名称后重试。

# 使用示例
examples:
  - intent: "查询Bug"
    query: "专利平台视觉优化的Bug情况"
    expected_flow: "查询流程"

  - intent: "创建Bug"
    query: "页面无法正常打开，判断为Bug"
    expected_flow: "创建流程"

  - intent: "创建Bug带图片"
    query: "登录页面加载失败，这是Bug，截图: http://xxx.com/screenshot.png"
    expected_flow: "创建流程（含图片）"

# 错误处理
error_handling:
  token_expired:
    action: "重新登录获取新Token"
    retry: 3

  api_timeout:
    action: "等待后重试"
    retry: 3
    interval: 100

  user_not_found:
    action: "提示用户检查输入的指派人姓名"

  network_error:
    action: "提示用户检查网络连接"
