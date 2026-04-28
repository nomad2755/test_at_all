/**
 * Airtest核心操作封装模块
 * 提供Airtest库的JavaScript封装接口
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class AirtestCore {
    constructor(config = {}) {
        this.deviceId = config.deviceId || null;
        this.logDir = config.logDir || './reports/logs';
        this.screenshotDir = config.screenshotDir || './reports/screenshots';
        this.timeout = config.timeout || 30000;

        // 确保目录存在
        this._ensureDirs();
    }

    /**
     * 确保必要的目录存在
     */
    _ensureDirs() {
        [this.logDir, this.screenshotDir].forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }

    /**
     * 执行Python命令
     */
    _execPython(code) {
        const escapedCode = code.replace(/"/g, '\\"');
        const deviceArg = this.deviceId ? `--device Android:///${this.deviceId}` : '';

        try {
            const result = execSync(
                `python -c "${escapedCode}" ${deviceArg}`,
                { timeout: this.timeout, encoding: 'utf-8' }
            );
            return { success: true, output: result };
        } catch (error) {
            return { success: false, error: error.message, output: error.stdout };
        }
    }

    /**
     * 点击操作
     * @param {Object|string} target - 点击目标，可以是文本、图片路径或坐标
     * @param {Object} options - 点击选项
     */
    async click(target, options = {}) {
        let code;
        const timeout = options.timeout || 20;

        if (typeof target === 'string') {
            // 判断是图片路径还是文本
            if (target.endsWith('.png') || target.endsWith('.jpg')) {
                code = `
from airtest.core.api import *
try:
    touch(Template(r"${target}"), timeout=${timeout})
    print("SUCCESS: Clicked image ${target}")
except Exception as e:
    print(f"ERROR: {e}")
`;
            } else {
                // 文本点击
                code = `
from airtest.core.api import *
try:
    touch(text("${target}"), timeout=${timeout})
    print("SUCCESS: Clicked text '${target}'")
except Exception as e:
    print(f"ERROR: {e}")
`;
            }
        } else if (typeof target === 'object') {
            if (target.x !== undefined && target.y !== undefined) {
                // 坐标点击
                code = `
from airtest.core.api import *
try:
    touch((${target.x}, ${target.y}))
    print("SUCCESS: Clicked coordinates (${target.x}, ${target.y})")
except Exception as e:
    print(f"ERROR: {e}")
`;
            } else if (target.image) {
                // 图片对象
                code = `
from airtest.core.api import *
try:
    touch(Template(r"${target.image}"), timeout=${timeout})
    print("SUCCESS: Clicked image")
except Exception as e:
    print(f"ERROR: {e}")
`;
            }
        }

        return this._execPython(code);
    }

    /**
     * 滑动操作
     * @param {Object} from - 起始位置
     * @param {Object} to - 结束位置
     * @param {Object} options - 滑动选项
     */
    async swipe(from, to, options = {}) {
        const duration = options.duration || 0.5;
        const steps = options.steps || 5;

        const code = `
from airtest.core.api import *
try:
    swipe((${from.x}, ${from.y}), (${to.x}, ${to.y}), duration=${duration}, steps=${steps})
    print("SUCCESS: Swiped from (${from.x}, ${from.y}) to (${to.x}, ${to.y})")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 滑动方向操作
     * @param {string} direction - 滑动方向 (up, down, left, right)
     */
    async swipeDirection(direction) {
        const code = `
from airtest.core.api import *
try:
    swipe_${direction}()
    print("SUCCESS: Swiped ${direction}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 输入文本
     * @param {string} text - 要输入的文本
     */
    async inputText(text) {
        const code = `
from airtest.core.api import *
try:
    text("${text}")
    print("SUCCESS: Input text '${text}'")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 截图
     * @param {string} filename - 截图文件名
     */
    async snapshot(filename) {
        const filepath = path.join(this.screenshotDir, filename);

        const code = `
from airtest.core.api import *
try:
    snapshot(filename=r"${filepath}")
    print("SUCCESS: Snapshot saved to ${filepath}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 等待元素出现
     * @param {Object|string} target - 等待目标
     * @param {number} timeout - 超时时间
     */
    async wait(target, timeout = 30) {
        let code;

        if (typeof target === 'string') {
            if (target.endsWith('.png') || target.endsWith('.jpg')) {
                code = `
from airtest.core.api import *
try:
    wait(Template(r"${target}"), timeout=${timeout})
    print("SUCCESS: Waited for image ${target}")
except Exception as e:
    print(f"ERROR: {e}")
`;
            } else {
                code = `
from airtest.core.api import *
try:
    wait(text("${target}"), timeout=${timeout})
    print("SUCCESS: Waited for text '${target}'")
except Exception as e:
    print(f"ERROR: {e}")
`;
            }
        }

        return this._execPython(code);
    }

    /**
     * 检查元素是否存在
     * @param {Object|string} target - 检查目标
     */
    async exists(target) {
        let code;

        if (typeof target === 'string') {
            if (target.endsWith('.png') || target.endsWith('.jpg')) {
                code = `
from airtest.core.api import *
result = exists(Template(r"${target}"))
if result:
    print(f"EXISTS: True, position: {result}")
else:
    print("EXISTS: False")
`;
            } else {
                code = `
from airtest.core.api import *
result = exists(text("${target}"))
if result:
    print(f"EXISTS: True, position: {result}")
else:
    print("EXISTS: False")
`;
            }
        }

        const result = this._execPython(code);
        return {
            ...result,
            exists: result.output?.includes('EXISTS: True')
        };
    }

    /**
     * 获取当前屏幕文本
     */
    async getScreenText() {
        const code = `
from airtest.core.api import *
try:
    result = ocr()
    print(f"TEXT: {result}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 键盘操作
     * @param {string} key - 按键名称
     */
    async keyevent(key) {
        const code = `
from airtest.core.api import *
try:
    keyevent("${key}")
    print("SUCCESS: Pressed key ${key}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 断言存在
     * @param {Object|string} target - 断言目标
     * @param {string} message - 断言失败消息
     */
    async assertExists(target, message = '') {
        let code;

        if (typeof target === 'string') {
            if (target.endsWith('.png') || target.endsWith('.jpg')) {
                code = `
from airtest.core.api import *
try:
    assert_exists(Template(r"${target}"), "${message}")
    print("ASSERT: PASSED - Element exists")
except Exception as e:
    print(f"ASSERT: FAILED - {e}")
`;
            } else {
                code = `
from airtest.core.api import *
try:
    assert_exists(text("${target}"), "${message}")
    print("ASSERT: PASSED - Element exists")
except Exception as e:
    print(f"ASSERT: FAILED - {e}")
`;
            }
        }

        const result = this._execPython(code);
        return {
            ...result,
            passed: result.output?.includes('ASSERT: PASSED')
        };
    }

    /**
     * 断言相等
     * @param {any} actual - 实际值
     * @param {any} expected - 期望值
     * @param {string} message - 断言消息
     */
    assertEqual(actual, expected, message = '') {
        return {
            passed: actual === expected,
            message: message || `Expected ${expected}, got ${actual}`
        };
    }

    /**
     * 连接设备
     * @param {string} deviceId - 设备ID
     */
    async connectDevice(deviceId) {
        this.deviceId = deviceId;

        const code = `
from airtest.core.api import *
try:
    connect_device("Android:///${deviceId}")
    print(f"SUCCESS: Connected to device ${deviceId}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }

    /**
     * 获取设备信息
     */
    async getDeviceInfo() {
        const code = `
from airtest.core.api import *
try:
    device = device()
    print(f"DEVICE: {device}")
except Exception as e:
    print(f"ERROR: {e}")
`;

        return this._execPython(code);
    }
}

// 导出模块
module.exports = AirtestCore;

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    const core = new AirtestCore({
        deviceId: process.env.DEVICE_ID,
        logDir: process.env.LOG_DIR || './reports/logs',
        screenshotDir: process.env.SCREENSHOT_DIR || './reports/screenshots'
    });

    const handleCommand = async () => {
        switch (command) {
            case 'click':
                const target = args[1];
                console.log(await core.click(target));
                break;
            case 'swipe':
                console.log(await core.swipe(
                    { x: parseInt(args[1]), y: parseInt(args[2]) },
                    { x: parseInt(args[3]), y: parseInt(args[4]) }
                ));
                break;
            case 'text':
                console.log(await core.inputText(args[1]));
                break;
            case 'snapshot':
                console.log(await core.snapshot(args[1] || `screenshot_${Date.now()}.png`));
                break;
            case 'wait':
                console.log(await core.wait(args[1], parseInt(args[2] || 30)));
                break;
            case 'exists':
                console.log(await core.exists(args[1]));
                break;
            case 'keyevent':
                console.log(await core.keyevent(args[1]));
                break;
            default:
                console.log('Available commands: click, swipe, text, snapshot, wait, exists, keyevent');
        }
    };

    handleCommand().catch(console.error);
}
