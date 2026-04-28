/**
 * ADB命令控制器
 * 提供Android设备ADB操作的封装接口
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class ADBController {
    constructor(config = {}) {
        this.adbPath = config.adbPath || 'adb';
        this.timeout = config.timeout || 60000;
        this.defaultDevice = config.defaultDevice || null;
    }

    /**
     * 执行ADB命令
     */
    _exec(command, options = {}) {
        const deviceId = options.device || this.defaultDevice;
        const deviceArg = deviceId ? `-s ${deviceId}` : '';
        const fullCommand = `${this.adbPath} ${deviceArg} ${command}`;

        try {
            const result = execSync(fullCommand, {
                timeout: options.timeout || this.timeout,
                encoding: 'utf-8',
                stdio: ['pipe', 'pipe', 'pipe']
            });
            return { success: true, output: result.trim(), command: fullCommand };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                output: error.stdout?.toString() || '',
                stderr: error.stderr?.toString() || '',
                command: fullCommand
            };
        }
    }

    /**
     * 列出所有连接的设备
     */
    listDevices() {
        const result = this._exec('devices -l');
        if (!result.success) return result;

        const lines = result.output.split('\n').slice(1);
        const devices = lines
            .filter(line => line.trim())
            .map(line => {
                const parts = line.trim().split(/\s+/);
                const id = parts[0];
                const status = parts[1];

                // 解析设备信息
                const info = {};
                for (let i = 2; i < parts.length; i++) {
                    const [key, value] = parts[i].split(':');
                    if (key && value) info[key] = value;
                }

                return { id, status, ...info };
            });

        return { ...result, devices };
    }

    /**
     * 安装应用
     * @param {string} apkPath - APK文件路径
     * @param {Object} options - 安装选项
     */
    install(apkPath, options = {}) {
        const args = [];

        if (options.allowDowngrade) args.push('-d');
        if (options.grantPermissions) args.push('-g');
        if (options.replace) args.push('-r');

        const result = this._exec(`install ${args.join(' ')} "${apkPath}"`, {
            timeout: options.timeout || 120000
        });

        if (result.success) {
            result.installed = result.output.includes('Success');
        }

        return result;
    }

    /**
     * 卸载应用
     * @param {string} packageName - 包名
     * @param {boolean} keepData - 是否保留数据
     */
    uninstall(packageName, keepData = false) {
        const args = keepData ? '-k' : '';
        const result = this._exec(`uninstall ${args} ${packageName}`);

        if (result.success) {
            result.uninstalled = result.output.includes('Success');
        }

        return result;
    }

    /**
     * 启动应用
     * @param {string} packageName - 包名
     * @param {string} activity - Activity名称
     */
    startApp(packageName, activity) {
        const component = activity ? `${packageName}/${activity}` : packageName;
        return this._exec(`shell am start -n ${component}`);
    }

    /**
     * 停止应用
     * @param {string} packageName - 包名
     */
    stopApp(packageName) {
        return this._exec(`shell am force-stop ${packageName}`);
    }

    /**
     * 清除应用数据
     * @param {string} packageName - 包名
     */
    clearApp(packageName) {
        return this._exec(`shell pm clear ${packageName}`);
    }

    /**
     * 获取应用信息
     * @param {string} packageName - 包名
     */
    getAppInfo(packageName) {
        const result = this._exec(`shell dumpsys package ${packageName}`);

        if (result.success) {
            const info = {
                packageName,
                versionName: this._extractValue(result.output, 'versionName='),
                versionCode: this._extractValue(result.output, 'versionCode='),
                targetSdk: this._extractValue(result.output, 'targetSdk='),
                permissions: []
            };

            // 提取权限列表
            const permMatch = result.output.match(/requested permissions:\s*([\s\S]*?)(?=\n\n|\ninstall permissions:)/);
            if (permMatch) {
                info.permissions = permMatch[1]
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line);
            }

            result.appInfo = info;
        }

        return result;
    }

    /**
     * 从输出中提取值
     */
    _extractValue(output, prefix) {
        const match = output.match(new RegExp(prefix + '([^\\s\\n]+)'));
        return match ? match[1] : null;
    }

    /**
     * 列出已安装应用
     * @param {boolean} thirdParty - 只列出第三方应用
     */
    listApps(thirdParty = false) {
        const flag = thirdParty ? '-3' : '';
        const result = this._exec(`shell pm list packages ${flag}`);

        if (result.success) {
            result.apps = result.output
                .split('\n')
                .filter(line => line.startsWith('package:'))
                .map(line => line.replace('package:', '').trim());
        }

        return result;
    }

    /**
     * 推送文件到设备
     * @param {string} localPath - 本地文件路径
     * @param {string} remotePath - 设备目标路径
     */
    push(localPath, remotePath) {
        return this._exec(`push "${localPath}" "${remotePath}"`);
    }

    /**
     * 从设备拉取文件
     * @param {string} remotePath - 设备文件路径
     * @param {string} localPath - 本地目标路径
     */
    pull(remotePath, localPath) {
        return this._exec(`pull "${remotePath}" "${localPath}"`);
    }

    /**
     * 执行Shell命令
     * @param {string} command - Shell命令
     */
    shell(command) {
        return this._exec(`shell ${command}`);
    }

    /**
     * 截屏
     * @param {string} localPath - 本地保存路径
     */
    screenshot(localPath) {
        const remotePath = '/sdcard/screenshot.png';

        // 截屏并拉取
        this._exec(`shell screencap -p ${remotePath}`);
        const result = this.pull(remotePath, localPath);

        // 清理临时文件
        this._exec(`shell rm ${remotePath}`);

        return result;
    }

    /**
     * 录屏
     * @param {Object} options - 录屏选项
     */
    startRecording(options = {}) {
        const time = options.time || 180;
        const bitrate = options.bitrate || 4000000;
        const remotePath = options.remotePath || '/sdcard/record.mp4';

        // 录屏是异步操作，使用spawn
        const deviceId = options.device || this.defaultDevice;
        const deviceArg = deviceId ? `-s ${deviceId}` : '';

        this.recordingProcess = spawn(
            this.adbPath,
            [...(deviceId ? ['-s', deviceId] : []), 'shell', 'screenrecord', '--time-limit', String(time), '--bit-rate', String(bitrate), remotePath]
        );

        return {
            success: true,
            message: 'Recording started',
            remotePath
        };
    }

    /**
     * 停止录屏并保存
     * @param {string} localPath - 本地保存路径
     * @param {string} remotePath - 设备录屏文件路径
     */
    stopRecording(localPath, remotePath = '/sdcard/record.mp4') {
        if (this.recordingProcess) {
            this.recordingProcess.kill('SIGINT');
            this.recordingProcess = null;
        }

        // 等待文件写入完成
        return new Promise(resolve => {
            setTimeout(() => {
                const result = this.pull(remotePath, localPath);
                this._exec(`shell rm ${remotePath}`);
                resolve(result);
            }, 1000);
        });
    }

    /**
     * 抓取日志
     * @param {Object} options - 日志选项
     */
    logcat(options = {}) {
        const args = [];

        if (options.tag) args.push(`${options.tag}:V`);
        if (options.package) {
            // 获取应用PID
            const pidResult = this._exec(`shell pidof ${options.package}`);
            if (pidResult.success && pidResult.output) {
                args.push(`--pid=${pidResult.output.trim()}`);
            }
        }
        args.push('*:S'); // 静默其他日志

        const result = this._exec(`logcat -d ${args.join(' ')}`, {
            timeout: options.timeout || 30000
        });

        if (options.clear) {
            this._exec('logcat -c');
        }

        return result;
    }

    /**
     * 清除日志
     */
    clearLogcat() {
        return this._exec('logcat -c');
    }

    /**
     * 获取设备属性
     * @param {string} property - 属性名称
     */
    getProperty(property) {
        const result = this._exec(`shell getprop ${property}`);
        return result;
    }

    /**
     * 获取设备详细信息
     */
    getDeviceInfo() {
        const properties = [
            'ro.product.model',
            'ro.product.brand',
            'ro.product.name',
            'ro.build.version.release',
            'ro.build.version.sdk',
            'ro.build.display.id'
        ];

        const info = {};
        properties.forEach(prop => {
            const result = this.getProperty(prop);
            if (result.success) {
                info[prop.replace(/ro\.product\.|ro\.build\.version\./g, '')] = result.output;
            }
        });

        // 获取屏幕分辨率
        const sizeResult = this._exec('shell wm size');
        if (sizeResult.success) {
            info.screenSize = sizeResult.output.replace('Physical size: ', '');
        }

        // 获取屏幕密度
        const densityResult = this._exec('shell wm density');
        if (densityResult.success) {
            info.screenDensity = densityResult.output.replace('Physical density: ', '');
        }

        return { success: true, deviceInfo: info };
    }

    /**
     * 重启设备
     * @param {string} mode - 重启模式 (normal, recovery, bootloader)
     */
    reboot(mode = 'normal') {
        const arg = mode === 'normal' ? '' : mode;
        return this._exec(`reboot ${arg}`);
    }

    /**
     * 输入文本
     * @param {string} text - 要输入的文本
     */
    inputText(text) {
        // AShell input text 不支持中文，需要使用广播方式
        const escaped = text.replace(/\s/g, '%s').replace(/'/g, "\\'");
        return this._exec(`shell input text '${escaped}'`);
    }

    /**
     * 模拟点击
     * @param {number} x - X坐标
     * @param {number} y - Y坐标
     */
    tap(x, y) {
        return this._exec(`shell input tap ${x} ${y}`);
    }

    /**
     * 模拟滑动
     * @param {number} x1 - 起始X
     * @param {number} y1 - 起始Y
     * @param {number} x2 - 结束X
     * @param {number} y2 - 结束Y
     * @param {number} duration - 持续时间(ms)
     */
    swipe(x1, y1, x2, y2, duration = 300) {
        return this._exec(`shell input swipe ${x1} ${y1} ${x2} ${y2} ${duration}`);
    }

    /**
     * 按键操作
     * @param {number|string} key - 按键码或名称
     */
    keyevent(key) {
        return this._exec(`shell input keyevent ${key}`);
    }
}

// 导出模块
module.exports = ADBController;

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    const adb = new ADBController({
        defaultDevice: process.env.DEVICE_ID
    });

    const handleCommand = async () => {
        switch (command) {
            case 'devices':
                console.log(JSON.stringify(adb.listDevices(), null, 2));
                break;
            case 'install':
                console.log(JSON.stringify(adb.install(args[1], { replace: true }), null, 2));
                break;
            case 'uninstall':
                console.log(JSON.stringify(adb.uninstall(args[1]), null, 2));
                break;
            case 'start':
                const [pkg, act] = args[1].split('/');
                console.log(JSON.stringify(adb.startApp(pkg, act), null, 2));
                break;
            case 'stop':
                console.log(JSON.stringify(adb.stopApp(args[1]), null, 2));
                break;
            case 'info':
                console.log(JSON.stringify(adb.getDeviceInfo(), null, 2));
                break;
            case 'apps':
                console.log(JSON.stringify(adb.listApps(true), null, 2));
                break;
            case 'logcat':
                console.log(JSON.stringify(adb.logcat({ package: args[1] }), null, 2));
                break;
            case 'screenshot':
                console.log(JSON.stringify(adb.screenshot(args[1]), null, 2));
                break;
            default:
                console.log('Available commands: devices, install, uninstall, start, stop, info, apps, logcat, screenshot');
        }
    };

    handleCommand().catch(console.error);
}
