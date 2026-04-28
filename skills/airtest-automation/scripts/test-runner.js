/**
 * 测试脚本执行器
 * 执行Airtest测试脚本并生成报告
 */

const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class TestRunner {
    constructor(config = {}) {
        this.testDir = config.testDir || path.join(__dirname, '../tests');
        this.reportDir = config.reportDir || path.join(__dirname, '../reports');
        this.logDir = path.join(this.reportDir, 'logs');
        this.screenshotDir = path.join(this.reportDir, 'screenshots');
        this.htmlDir = path.join(this.reportDir, 'html');

        this._ensureDirs();
    }

    /**
     * 确保目录存在
     */
    _ensureDirs() {
        [this.logDir, this.screenshotDir, this.htmlDir].forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }

    /**
     * 执行测试脚本
     * @param {string} scriptPath - 脚本路径
     * @param {Object} options - 执行选项
     */
    async run(scriptPath, options = {}) {
        const startTime = Date.now();
        const testId = `test_${Date.now()}`;

        // 解析脚本路径
        const absolutePath = path.isAbsolute(scriptPath)
            ? scriptPath
            : path.join(this.testDir, scriptPath);

        if (!fs.existsSync(absolutePath)) {
            return {
                success: false,
                error: `脚本不存在: ${absolutePath}`,
                testId
            };
        }

        // 构建执行命令
        const args = ['run', absolutePath];

        // 添加设备参数
        if (options.deviceId) {
            args.push('--device', `Android:///${options.deviceId}`);
        }

        // 添加日志目录
        const logPath = path.join(this.logDir, testId);
        args.push('--log', logPath);

        // 执行测试
        const result = {
            testId,
            scriptPath: absolutePath,
            startTime: new Date().toISOString(),
            status: 'running',
            logs: [],
            screenshots: []
        };

        try {
            // 使用airtest命令行工具执行
            const output = execSync(`airtest ${args.join(' ')}`, {
                timeout: options.timeout || 300000,
                encoding: 'utf-8',
                cwd: path.dirname(absolutePath)
            });

            result.status = 'passed';
            result.output = output;
            result.endTime = new Date().toISOString();
            result.duration = Date.now() - startTime;

            // 收集截图
            result.screenshots = this._collectScreenshots(logPath);

        } catch (error) {
            result.status = 'failed';
            result.error = error.message;
            result.output = error.stdout?.toString() || '';
            result.stderr = error.stderr?.toString() || '';
            result.endTime = new Date().toISOString();
            result.duration = Date.now() - startTime;

            // 即使失败也要收集截图
            result.screenshots = this._collectScreenshots(logPath);
        }

        // 生成报告
        const report = await this.generateReport(result);

        return {
            ...result,
            report
        };
    }

    /**
     * 收集截图
     */
    _collectScreenshots(logPath) {
        const screenshots = [];

        if (!fs.existsSync(logPath)) return screenshots;

        const files = fs.readdirSync(logPath);
        files.forEach(file => {
            if (file.endsWith('.png') || file.endsWith('.jpg')) {
                screenshots.push({
                    name: file,
                    path: path.join(logPath, file)
                });
            }
        });

        return screenshots;
    }

    /**
     * 生成测试报告
     * @param {Object} result - 测试结果
     */
    async generateReport(result) {
        const reportPath = path.join(this.htmlDir, `${result.testId}.html`);

        const html = this._generateHtmlReport(result);
        fs.writeFileSync(reportPath, html, 'utf-8');

        return {
            path: reportPath,
            url: `file://${reportPath}`
        };
    }

    /**
     * 生成HTML报告
     */
    _generateHtmlReport(result) {
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试报告 - ${result.testId}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .header h1 { font-size: 24px; margin-bottom: 10px; }
        .header .meta { opacity: 0.9; font-size: 14px; }
        .content { padding: 20px; }
        .section { margin-bottom: 20px; }
        .section h2 {
            font-size: 18px;
            color: #333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
        }
        .status.passed { background: #d4edda; color: #155724; }
        .status.failed { background: #f8d7da; color: #721c24; }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }
        .info-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }
        .info-item label {
            display: block;
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }
        .info-item value {
            display: block;
            font-size: 14px;
            color: #333;
        }
        .log {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        .screenshots {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }
        .screenshot {
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }
        .screenshot img {
            width: 100%;
            display: block;
        }
        .screenshot .name {
            padding: 10px;
            background: #f8f9fa;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>测试报告</h1>
            <div class="meta">
                <span>测试ID: ${result.testId}</span> |
                <span>执行时间: ${result.startTime}</span>
            </div>
        </div>
        <div class="content">
            <div class="section">
                <h2>测试概览</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>执行状态</label>
                        <value><span class="status ${result.status}">${result.status.toUpperCase()}</span></value>
                    </div>
                    <div class="info-item">
                        <label>执行耗时</label>
                        <value>${result.duration ? (result.duration / 1000).toFixed(2) + 's' : 'N/A'}</value>
                    </div>
                    <div class="info-item">
                        <label>脚本路径</label>
                        <value>${result.scriptPath}</value>
                    </div>
                    <div class="info-item">
                        <label>结束时间</label>
                        <value>${result.endTime || 'N/A'}</value>
                    </div>
                </div>
            </div>

            ${result.screenshots.length > 0 ? `
            <div class="section">
                <h2>截图 (${result.screenshots.length})</h2>
                <div class="screenshots">
                    ${result.screenshots.map(s => `
                    <div class="screenshot">
                        <img src="file://${s.path}" alt="${s.name}">
                        <div class="name">${s.name}</div>
                    </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}

            <div class="section">
                <h2>执行日志</h2>
                <div class="log">${this._escapeHtml(result.output || result.error || 'No output')}</div>
            </div>
        </div>
    </div>
</body>
</html>`;
    }

    /**
     * HTML转义
     */
    _escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * 运行所有测试
     * @param {Object} options - 执行选项
     */
    async runAll(options = {}) {
        const results = [];
        const testFiles = this._findAllTests();

        for (const testFile of testFiles) {
            console.log(`Running: ${testFile}`);
            const result = await this.run(testFile, options);
            results.push(result);
        }

        return {
            total: testFiles.length,
            passed: results.filter(r => r.status === 'passed').length,
            failed: results.filter(r => r.status === 'failed').length,
            results
        };
    }

    /**
     * 查找所有测试文件
     */
    _findAllTests() {
        const tests = [];

        const scanDir = (dir) => {
            if (!fs.existsSync(dir)) return;

            const files = fs.readdirSync(dir);
            files.forEach(file => {
                const fullPath = path.join(dir, file);
                const stat = fs.statSync(fullPath);

                if (stat.isDirectory()) {
                    scanDir(fullPath);
                } else if (file.endsWith('.air.py')) {
                    tests.push(path.relative(this.testDir, fullPath));
                }
            });
        };

        scanDir(this.testDir);
        return tests;
    }

    /**
     * 并行执行测试
     * @param {Array} scriptPaths - 脚本路径列表
     * @param {Object} options - 执行选项
     */
    async runParallel(scriptPaths, options = {}) {
        const promises = scriptPaths.map(scriptPath =>
            this.run(scriptPath, options)
        );

        return Promise.all(promises);
    }
}

// 导出模块
module.exports = TestRunner;

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    const runner = new TestRunner();

    const handleCommand = async () => {
        if (args[0] === 'run') {
            const result = await runner.run(args[1]);
            console.log(JSON.stringify(result, null, 2));
        } else if (args[0] === 'run-all') {
            const results = await runner.runAll();
            console.log(JSON.stringify(results, null, 2));
        } else {
            console.log('Usage: node test-runner.js run <script_path>');
            console.log('       node test-runner.js run-all');
        }
    };

    handleCommand().catch(console.error);
}
