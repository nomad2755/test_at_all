/**
 * 参数验证器
 * 验证测试脚本参数和配置
 */

class Validator {
    constructor() {
        this.rules = {
            // 必填规则
            required: (value) => value !== null && value !== undefined && value !== '',

            // 类型规则
            string: (value) => typeof value === 'string',
            number: (value) => typeof value === 'number' && !isNaN(value),
            boolean: (value) => typeof value === 'boolean',
            object: (value) => typeof value === 'object' && value !== null,
            array: (value) => Array.isArray(value),

            // 格式规则
            email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
            url: (value) => /^https?:\/\/.+/.test(value),
            packageName: (value) => /^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$/.test(value),
            deviceId: (value) => /^[a-zA-Z0-9:_-]+$/.test(value),

            // 范围规则
            minLength: (value, min) => value.length >= min,
            maxLength: (value, max) => value.length <= max,
            min: (value, min) => value >= min,
            max: (value, max) => value <= max,

            // 文件规则
            fileExists: (value) => {
                const fs = require('fs');
                try {
                    return fs.existsSync(value);
                } catch {
                    return false;
                }
            },
            fileExtension: (value, ext) => value.endsWith(ext),

            // 枚举规则
            enum: (value, values) => values.includes(value)
        };
    }

    /**
     * 验证单个值
     * @param {any} value - 要验证的值
     * @param {Object} schema - 验证规则
     */
    validateValue(value, schema) {
        const errors = [];

        for (const [ruleName, ruleParam] of Object.entries(schema)) {
            const rule = this.rules[ruleName];

            if (!rule) {
                errors.push(`未知规则: ${ruleName}`);
                continue;
            }

            // 跳过非必填的空值
            if (ruleName !== 'required' && !schema.required && (value === null || value === undefined || value === '')) {
                continue;
            }

            // 执行验证
            const isValid = ruleParam === true
                ? rule(value)
                : rule(value, ruleParam);

            if (!isValid) {
                errors.push(this._formatError(ruleName, ruleParam));
            }
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }

    /**
     * 格式化错误消息
     */
    _formatError(ruleName, ruleParam) {
        const messages = {
            required: '此字段为必填项',
            string: '必须是字符串',
            number: '必须是数字',
            boolean: '必须是布尔值',
            object: '必须是对象',
            array: '必须是数组',
            email: '邮箱格式不正确',
            url: 'URL格式不正确',
            packageName: '包名格式不正确',
            deviceId: '设备ID格式不正确',
            minLength: `长度不能少于${ruleParam}`,
            maxLength: `长度不能超过${ruleParam}`,
            min: `不能小于${ruleParam}`,
            max: `不能大于${ruleParam}`,
            fileExists: '文件不存在',
            fileExtension: `文件扩展名必须是${ruleParam}`,
            enum: `必须是以下值之一: ${ruleParam.join(', ')}`
        };

        return messages[ruleName] || `验证失败: ${ruleName}`;
    }

    /**
     * 验证对象
     * @param {Object} obj - 要验证的对象
     * @param {Object} schema - 验证规则
     */
    validateObject(obj, schema) {
        const result = { valid: true, errors: {} };

        for (const [field, rules] of Object.entries(schema)) {
            const value = obj[field];
            const fieldResult = this.validateValue(value, rules);

            if (!fieldResult.valid) {
                result.valid = false;
                result.errors[field] = fieldResult.errors;
            }
        }

        return result;
    }

    /**
     * 验证测试脚本配置
     */
    validateTestConfig(config) {
        const schema = {
            deviceId: { string: true, deviceId: true },
            packageName: { required: true, string: true, packageName: true },
            timeout: { number: true, min: 1, max: 300 },
            logDir: { string: true },
            screenshotDir: { string: true }
        };

        return this.validateObject(config, schema);
    }

    /**
     * 验证ADB命令参数
     */
    validateAdbParams(command, params) {
        const schemas = {
            install: {
                apkPath: { required: true, string: true, fileExists: true, fileExtension: '.apk' }
            },
            uninstall: {
                packageName: { required: true, string: true, packageName: true }
            },
            start: {
                packageName: { required: true, string: true, packageName: true },
                activity: { string: true }
            },
            stop: {
                packageName: { required: true, string: true, packageName: true }
            }
        };

        const schema = schemas[command];
        if (!schema) {
            return { valid: true, errors: {} };
        }

        return this.validateObject(params, schema);
    }

    /**
     * 验证测试步骤
     */
    validateStep(step) {
        const errors = [];

        // 检查必要字段
        if (!step.action) {
            errors.push('缺少action字段');
        }

        // 根据动作类型验证
        switch (step.action) {
            case 'click':
                if (!step.target) {
                    errors.push('click操作需要target');
                }
                break;

            case 'input':
                if (!step.target) {
                    errors.push('input操作需要target');
                }
                if (step.value === undefined || step.value === null) {
                    errors.push('input操作需要value');
                }
                break;

            case 'swipe':
                if (!step.direction && !step.from && !step.to) {
                    errors.push('swipe操作需要direction或from/to坐标');
                }
                break;

            case 'wait':
                if (!step.target) {
                    errors.push('wait操作需要target');
                }
                if (step.timeout && (typeof step.timeout !== 'number' || step.timeout < 0)) {
                    errors.push('timeout必须是非负数');
                }
                break;

            case 'assert':
                if (!step.target) {
                    errors.push('assert操作需要target');
                }
                break;
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }

    /**
     * 验证测试脚本
     */
    validateScript(script) {
        const result = { valid: true, errors: [] };

        // 检查脚本内容
        if (!script || !script.trim()) {
            result.valid = false;
            result.errors.push('脚本内容为空');
            return result;
        }

        // 检查必要的导入
        if (!script.includes('from airtest.core.api import')) {
            result.errors.push('缺少airtest导入语句');
        }

        // 检查语法错误 (简单的正则检查)
        const syntaxChecks = [
            { pattern: /def\s+\w+\s*\([^)]*\)\s*:/, message: '函数定义语法检查' },
            { pattern: /if\s+.+:\s*$/, message: 'if语句语法检查', multiline: true },
            { pattern: /try:\s*$/, message: 'try语句语法检查', multiline: true },
            { pattern: /except.*:\s*$/, message: 'except语句语法检查', multiline: true }
        ];

        // 检查括号匹配
        const openBrackets = (script.match(/\(/g) || []).length;
        const closeBrackets = (script.match(/\)/g) || []).length;
        if (openBrackets !== closeBrackets) {
            result.errors.push('括号不匹配');
        }

        result.valid = result.errors.length === 0;
        return result;
    }

    /**
     * 添加自定义规则
     */
    addRule(name, validator) {
        if (typeof validator !== 'function') {
            throw new Error('验证器必须是函数');
        }
        this.rules[name] = validator;
    }
}

module.exports = Validator;
