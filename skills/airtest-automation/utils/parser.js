/**
 * 自然语言解析器
 * 解析自然语言测试描述
 */

class Parser {
    constructor() {
        // 操作关键词
        this.actionKeywords = {
            click: ['点击', '单击', '按', 'tap', 'click', 'press'],
            doubleClick: ['双击', 'double tap', 'double click'],
            longPress: ['长按', '长点击', 'long press'],
            input: ['输入', '填写', 'type', 'input', 'enter', '填写'],
            swipe: ['滑动', '滑', 'swipe', 'scroll', '拖动'],
            wait: ['等待', '等', 'wait', 'sleep'],
            screenshot: ['截图', '截屏', 'screenshot', 'capture'],
            verify: ['验证', '检查', '断言', 'verify', 'assert', 'check'],
            exists: ['存在', '出现', '显示', 'visible', 'exists']
        };

        // 方向关键词
        this.directionKeywords = {
            up: ['上', '向上', 'up', 'top'],
            down: ['下', '向下', 'down', 'bottom'],
            left: ['左', '向左', 'left'],
            right: ['右', '向右', 'right']
        };

        // 时间单位
        this.timeUnits = {
            ms: ['毫秒', 'ms', 'millisecond'],
            s: ['秒', 's', 'sec', 'second'],
            m: ['分', 'm', 'min', 'minute']
        };
    }

    /**
     * 解析测试描述
     * @param {string} description - 测试描述
     */
    parse(description) {
        const sentences = this._splitSentences(description);
        const steps = sentences.map((sentence, index) => this._parseSentence(sentence, index));

        return {
            raw: description,
            steps: steps.filter(s => s !== null),
            sentenceCount: sentences.length
        };
    }

    /**
     * 分割句子
     */
    _splitSentences(text) {
        return text
            .split(/[。；\n，,]/)
            .map(s => s.trim())
            .filter(s => s.length > 0);
    }

    /**
     * 解析单个句子
     */
    _parseSentence(sentence, index) {
        const action = this._detectAction(sentence);
        if (!action) return null;

        const result = {
            index: index + 1,
            raw: sentence,
            action: action.type,
            params: {}
        };

        // 根据动作类型提取参数
        switch (action.type) {
            case 'click':
            case 'doubleClick':
            case 'longPress':
                result.target = this._extractTarget(sentence);
                result.params = this._extractClickParams(sentence);
                break;

            case 'input':
                result.target = this._extractInputTarget(sentence);
                result.value = this._extractInputValue(sentence);
                break;

            case 'swipe':
                result.direction = this._extractDirection(sentence);
                result.params = this._extractSwipeParams(sentence);
                break;

            case 'wait':
                result.target = this._extractTarget(sentence);
                result.params = { timeout: this._extractTimeout(sentence) };
                break;

            case 'screenshot':
                result.params = { filename: this._extractFilename(sentence) };
                break;

            case 'verify':
            case 'exists':
                result.target = this._extractTarget(sentence);
                result.params = { expected: this._extractExpectedValue(sentence) };
                break;
        }

        return result;
    }

    /**
     * 检测动作类型
     */
    _detectAction(sentence) {
        const lower = sentence.toLowerCase();

        for (const [type, keywords] of Object.entries(this.actionKeywords)) {
            for (const keyword of keywords) {
                if (lower.includes(keyword)) {
                    return { type, keyword };
                }
            }
        }

        return null;
    }

    /**
     * 提取目标元素
     */
    _extractTarget(sentence) {
        // 提取引号内容
        const quoteMatch = sentence.match(/["'「『]([^"」』]+)["'」』]/);
        if (quoteMatch) {
            return {
                type: 'text',
                value: quoteMatch[1]
            };
        }

        // 提取坐标
        const coordMatch = sentence.match(/坐标\s*\(?\s*(\d+)\s*,\s*(\d+)\s*\)?/);
        if (coordMatch) {
            return {
                type: 'coordinate',
                x: parseInt(coordMatch[1]),
                y: parseInt(coordMatch[2])
            };
        }

        // 提取图片路径
        const imageMatch = sentence.match(/图片\s*["']?([^"'\s]+\.png|jpg)["']?/i);
        if (imageMatch) {
            return {
                type: 'image',
                path: imageMatch[1]
            };
        }

        return { type: 'unknown', value: sentence };
    }

    /**
     * 提取点击参数
     */
    _extractClickParams(sentence) {
        const params = {};

        // 提取次数
        const countMatch = sentence.match(/(\d+)\s*次/);
        if (countMatch) {
            params.times = parseInt(countMatch[1]);
        }

        // 提取持续时间
        const durationMatch = sentence.match(/持续\s*(\d+)\s*(毫秒|秒|ms|s)/);
        if (durationMatch) {
            params.duration = this._convertToMs(parseInt(durationMatch[1]), durationMatch[2]);
        }

        return params;
    }

    /**
     * 提取输入目标
     */
    _extractInputTarget(sentence) {
        const match = sentence.match(/到\s*["'「『]([^"」』]+)["'」』]|在\s*["'「『]([^"」』]+)["'」』]/);
        if (match) {
            return match[1] || match[2];
        }
        return null;
    }

    /**
     * 提取输入值
     */
    _extractInputValue(sentence) {
        const match = sentence.match(/输入\s*["'「『]([^"」』]+)["'」』]|填写\s*["'「『]([^"」』]+)["'」』]/);
        if (match) {
            return match[1] || match[2];
        }
        return null;
    }

    /**
     * 提取方向
     */
    _extractDirection(sentence) {
        const lower = sentence.toLowerCase();

        for (const [direction, keywords] of Object.entries(this.directionKeywords)) {
            for (const keyword of keywords) {
                if (lower.includes(keyword)) {
                    return direction;
                }
            }
        }

        return null;
    }

    /**
     * 提取滑动参数
     */
    _extractSwipeParams(sentence) {
        const params = {};

        // 提取距离
        const distanceMatch = sentence.match(/(\d+)\s*(像素|px|距离)/);
        if (distanceMatch) {
            params.distance = parseInt(distanceMatch[1]);
        }

        // 提取持续时间
        const durationMatch = sentence.match(/持续?\s*(\d+)\s*(毫秒|秒|ms|s)/);
        if (durationMatch) {
            params.duration = this._convertToMs(parseInt(durationMatch[1]), durationMatch[2]);
        }

        return params;
    }

    /**
     * 提取超时时间
     */
    _extractTimeout(sentence) {
        const match = sentence.match(/(\d+)\s*(毫秒|秒|分|ms|s|m|min)/);
        if (match) {
            return this._convertToMs(parseInt(match[1]), match[2]);
        }
        return 20000; // 默认20秒
    }

    /**
     * 提取文件名
     */
    _extractFilename(sentence) {
        const match = sentence.match(/保存为\s*["'「『]?([^"」』\s]+)["'」』]?/);
        if (match) {
            return match[1];
        }
        return `screenshot_${Date.now()}.png`;
    }

    /**
     * 提取期望值
     */
    _extractExpectedValue(sentence) {
        const match = sentence.match(/期望?\s*["'「『]?([^"」』\s]+)["'」』]?|应该\s*["'「『]?([^"」』\s]+)["'」』]?/);
        if (match) {
            return match[1] || match[2];
        }
        return null;
    }

    /**
     * 转换为毫秒
     */
    _convertToMs(value, unit) {
        const lower = unit.toLowerCase();

        if (this.timeUnits.ms.some(u => lower.includes(u))) {
            return value;
        }
        if (this.timeUnits.s.some(u => lower.includes(u))) {
            return value * 1000;
        }
        if (this.timeUnits.m.some(u => lower.includes(u))) {
            return value * 60 * 1000;
        }

        return value;
    }

    /**
     * 验证解析结果
     */
    validate(parsed) {
        const errors = [];

        parsed.steps.forEach((step, index) => {
            if (!step.action) {
                errors.push(`步骤${index + 1}: 未识别的动作`);
            }

            if (['click', 'wait', 'verify'].includes(step.action) && !step.target) {
                errors.push(`步骤${index + 1}: 缺少目标元素`);
            }

            if (step.action === 'input' && !step.value) {
                errors.push(`步骤${index + 1}: 缺少输入值`);
            }
        });

        return {
            valid: errors.length === 0,
            errors
        };
    }
}

module.exports = Parser;
