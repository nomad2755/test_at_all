/**
 * 自然语言测试用例生成器
 * 根据自然语言描述生成Airtest测试脚本
 */

const fs = require('fs');
const path = require('path');

class TestGenerator {
    constructor(config = {}) {
        this.templateDir = config.templateDir || path.join(__dirname, '../templates');
        this.outputDir = config.outputDir || path.join(__dirname, '../tests');
        this.templates = this._loadTemplates();
    }

    /**
     * 加载模板文件
     */
    _loadTemplates() {
        const templates = {};
        const templateFiles = ['basic-test.air.py', 'login-test.air.py', 'workflow-test.air.py'];

        templateFiles.forEach(file => {
            const templatePath = path.join(this.templateDir, file);
            if (fs.existsSync(templatePath)) {
                templates[file.replace('.air.py', '')] = fs.readFileSync(templatePath, 'utf-8');
            }
        });

        return templates;
    }

    /**
     * 解析自然语言描述
     * @param {string} description - 测试描述
     */
    parseDescription(description) {
        const steps = [];
        const sentences = description.split(/[。；\n]/).filter(s => s.trim());

        // 操作关键词映射
        const actionPatterns = [
            { pattern: /点击["'](.+?)["']|点击(.+?)(?=，|然后|并|$)/, action: 'click', extractor: (match) => match[1] || match[2] },
            { pattern: /输入["'](.+?)["']到["'](.+?)["']|在["'](.+?)["']输入["'](.+?)["']/, action: 'input', extractor: (match) => ({ text: match[1] || match[4], target: match[2] || match[3] }) },
            { pattern: /滑动到["'](.+?)["']|向(上|下|左|右)滑动/, action: 'swipe', extractor: (match) => match[1] || match[2] },
            { pattern: /等待["'](.+?)["']出现|等待(.+?)(?=出现|显示)/, action: 'wait', extractor: (match) => match[1] || match[2] },
            { pattern: /截图|截屏/, action: 'screenshot', extractor: () => null },
            { pattern: /检查["'](.+?)["']是否存在|验证["'](.+?)["']存在/, action: 'exists', extractor: (match) => match[1] || match[2] },
            { pattern: /断言["'](.+?)["']存在/, action: 'assert', extractor: (match) => match[1] },
            { pattern: /启动应用["'](.+?)["']|打开(.+?)(?=应用|APP)/, action: 'start_app', extractor: (match) => match[1] || match[2] },
            { pattern: /关闭应用|退出应用/, action: 'stop_app', extractor: () => null },
            { pattern: /输入文字["'](.+?)["']/, action: 'input_text', extractor: (match) => match[1] },
        ];

        sentences.forEach((sentence, index) => {
            const trimmed = sentence.trim();
            if (!trimmed) return;

            for (const { pattern, action, extractor } of actionPatterns) {
                const match = trimmed.match(pattern);
                if (match) {
                    steps.push({
                        index: index + 1,
                        action,
                        target: extractor(match),
                        raw: trimmed,
                        params: this._extractParams(trimmed, action)
                    });
                    break;
                }
            }
        });

        return steps;
    }

    /**
     * 提取额外参数
     */
    _extractParams(sentence, action) {
        const params = {};

        // 提取超时时间
        const timeoutMatch = sentence.match(/超时(\d+)秒|等待(\d+)秒/);
        if (timeoutMatch) {
            params.timeout = parseInt(timeoutMatch[1] || timeoutMatch[2]);
        }

        // 提取坐标
        const coordMatch = sentence.match(/坐标\((\d+),\s*(\d+)\)/);
        if (coordMatch) {
            params.x = parseInt(coordMatch[1]);
            params.y = parseInt(coordMatch[2]);
        }

        return params;
    }

    /**
     * 生成Python测试代码
     * @param {Array} steps - 解析后的步骤
     * @param {Object} options - 生成选项
     */
    generateCode(steps, options = {}) {
        const lines = [];
        const imports = new Set(['from airtest.core.api import *']);

        // 添加文件头
        lines.push(`# -*- coding: utf-8 -*-`);
        lines.push(`# 自动生成的测试脚本`);
        lines.push(`# 生成时间: ${new Date().toISOString()}`);
        lines.push(`# 测试描述: ${options.description || 'N/A'}`);
        lines.push('');

        // 如果使用poco，添加导入
        if (steps.some(s => s.action === 'input' && typeof s.target === 'object')) {
            imports.add('from poco.drivers.android.uiautomation import AndroidUiautomationPoco');
        }

        lines.push(...Array.from(imports));
        lines.push('');

        // 连接设备
        if (options.deviceId) {
            lines.push(`# 连接设备`);
            lines.push(`connect_device("Android:///${options.deviceId}")`);
            lines.push('');
        }

        // 生成测试步骤
        lines.push(`# 测试步骤`);
        steps.forEach((step, index) => {
            lines.push(`# 步骤${index + 1}: ${step.raw}`);

            const codeLines = this._generateStepCode(step, imports);
            lines.push(...codeLines);
            lines.push('');
        });

        // 添加测试结束
        lines.push(`# 测试完成`);
        lines.push(`print("测试执行完成")`);

        return lines.join('\n');
    }

    /**
     * 生成单个步骤的代码
     */
    _generateStepCode(step, imports) {
        const lines = [];

        switch (step.action) {
            case 'click':
                if (typeof step.target === 'object' && step.target.x) {
                    lines.push(`touch((${step.target.x}, ${step.target.y}))`);
                } else if (step.target?.endsWith?.('.png')) {
                    lines.push(`touch(Template(r"${step.target}"))`);
                } else {
                    lines.push(`touch(text("${step.target}"))`);
                }
                break;

            case 'input':
                if (typeof step.target === 'object') {
                    lines.push(`poco("${step.target.target}").set_text("${step.target.text}")`);
                } else {
                    lines.push(`text("${step.target.text || step.target}")`);
                }
                break;

            case 'swipe':
                if (['up', 'down', 'left', 'right'].includes(step.target)) {
                    lines.push(`swipe_${step.target}()`);
                } else {
                    lines.push(`# TODO: 需要指定滑动坐标`);
                }
                break;

            case 'wait':
                const timeout = step.params.timeout || 20;
                if (step.target?.endsWith?.('.png')) {
                    lines.push(`wait(Template(r"${step.target}"), timeout=${timeout})`);
                } else {
                    lines.push(`wait(text("${step.target}"), timeout=${timeout})`);
                }
                break;

            case 'screenshot':
                const filename = `screenshot_${Date.now()}.png`;
                lines.push(`snapshot(filename="${filename}")`);
                break;

            case 'exists':
                if (step.target?.endsWith?.('.png')) {
                    lines.push(`result = exists(Template(r"${step.target}"))`);
                } else {
                    lines.push(`result = exists(text("${step.target}"))`);
                }
                lines.push(`print(f"元素存在: {result}")`);
                break;

            case 'assert':
                if (step.target?.endsWith?.('.png')) {
                    lines.push(`assert_exists(Template(r"${step.target}"), "元素应该存在")`);
                } else {
                    lines.push(`assert_exists(text("${step.target}"), "元素应该存在")`);
                }
                break;

            case 'start_app':
                lines.push(`start_app("${step.target}")`);
                break;

            case 'stop_app':
                lines.push(`stop_app("${step.target || 'current'}")`);
                break;

            case 'input_text':
                lines.push(`text("${step.target}")`);
                break;

            default:
                lines.push(`# 未知操作: ${step.action}`);
        }

        return lines;
    }

    /**
     * 根据描述生成完整测试脚本
     * @param {string} description - 测试描述
     * @param {Object} options - 生成选项
     */
    generate(description, options = {}) {
        // 解析描述
        const steps = this.parseDescription(description);

        // 生成代码
        const code = this.generateCode(steps, { ...options, description });

        // 确定输出路径
        const testType = options.type || 'custom';
        const testName = options.name || `test_${Date.now()}`;
        const category = this._categorizeTest(description);

        const outputPath = path.join(this.outputDir, category, `${testName}.air.py`);

        return {
            steps,
            code,
            outputPath,
            category
        };
    }

    /**
     * 根据描述分类测试
     */
    _categorizeTest(description) {
        const keywords = {
            auth: ['登录', '注册', '密码', '账号', 'login', 'auth', 'register'],
            payment: ['支付', '订单', '购买', '退款', 'payment', 'order'],
            common: ['冒烟', '通用', 'smoke', 'common']
        };

        for (const [category, words] of Object.entries(keywords)) {
            if (words.some(word => description.toLowerCase().includes(word))) {
                return category;
            }
        }

        return 'custom';
    }

    /**
     * 使用模板生成脚本
     * @param {string} templateName - 模板名称
     * @param {Object} params - 模板参数
     */
    generateFromTemplate(templateName, params = {}) {
        const template = this.templates[templateName];
        if (!template) {
            throw new Error(`模板 ${templateName} 不存在`);
        }

        // 替换模板变量
        let code = template;
        Object.entries(params).forEach(([key, value]) => {
            const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
            code = code.replace(regex, value);
        });

        return code;
    }

    /**
     * 保存生成的测试脚本
     * @param {string} code - 测试代码
     * @param {string} outputPath - 输出路径
     */
    save(code, outputPath) {
        const dir = path.dirname(outputPath);
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }

        fs.writeFileSync(outputPath, code, 'utf-8');

        return {
            success: true,
            path: outputPath,
            createdAt: new Date().toISOString()
        };
    }
}

// 导出模块
module.exports = TestGenerator;

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    const generator = new TestGenerator();

    if (args[0] === 'generate') {
        const description = args.slice(1).join(' ');
        const result = generator.generate(description);
        console.log(JSON.stringify(result, null, 2));
    } else if (args[0] === 'parse') {
        const description = args.slice(1).join(' ');
        const steps = generator.parseDescription(description);
        console.log(JSON.stringify(steps, null, 2));
    } else {
        console.log('Usage: node test-generator.js generate <description>');
        console.log('       node test-generator.js parse <description>');
    }
}
