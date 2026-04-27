/**
 * 测试脚本管理器
 * 管理测试脚本的增删改查和执行
 */

const fs = require('fs');
const path = require('path');
const TestRunner = require('./test-runner');
const TestGenerator = require('./test-generator');

class TestManager {
    constructor(config = {}) {
        this.testDir = config.testDir || path.join(__dirname, '../tests');
        this.reportDir = config.reportDir || path.join(__dirname, '../reports');
        this.metadataFile = path.join(this.testDir, 'metadata.json');

        this.runner = new TestRunner({ testDir: this.testDir, reportDir: this.reportDir });
        this.generator = new TestGenerator({ outputDir: this.testDir });

        this._ensureMetadata();
    }

    /**
     * 确保元数据文件存在
     */
    _ensureMetadata() {
        if (!fs.existsSync(this.metadataFile)) {
            fs.writeFileSync(this.metadataFile, JSON.stringify({
                tests: {},
                lastUpdated: new Date().toISOString()
            }, null, 2));
        }
    }

    /**
     * 读取元数据
     */
    _readMetadata() {
        try {
            return JSON.parse(fs.readFileSync(this.metadataFile, 'utf-8'));
        } catch {
            return { tests: {}, lastUpdated: new Date().toISOString() };
        }
    }

    /**
     * 写入元数据
     */
    _writeMetadata(data) {
        data.lastUpdated = new Date().toISOString();
        fs.writeFileSync(this.metadataFile, JSON.stringify(data, null, 2));
    }

    /**
     * 列出所有测试脚本
     * @param {Object} options - 查询选项
     */
    list(options = {}) {
        const tests = [];
        const metadata = this._readMetadata();

        const scanDir = (dir, category = '') => {
            if (!fs.existsSync(dir)) return;

            const files = fs.readdirSync(dir);
            files.forEach(file => {
                if (file === 'metadata.json') return;

                const fullPath = path.join(dir, file);
                const stat = fs.statSync(fullPath);

                if (stat.isDirectory()) {
                    scanDir(fullPath, file);
                } else if (file.endsWith('.air.py')) {
                    const relativePath = path.relative(this.testDir, fullPath);
                    const meta = metadata.tests[relativePath] || {};

                    tests.push({
                        name: file.replace('.air.py', ''),
                        path: relativePath,
                        category: category || 'root',
                        createdAt: meta.createdAt || stat.birthtime.toISOString(),
                        lastRun: meta.lastRun || null,
                        lastStatus: meta.lastStatus || null,
                        description: meta.description || '',
                        tags: meta.tags || []
                    });
                }
            });
        };

        scanDir(this.testDir);

        // 过滤
        if (options.category) {
            return tests.filter(t => t.category === options.category);
        }
        if (options.status) {
            return tests.filter(t => t.lastStatus === options.status);
        }
        if (options.tag) {
            return tests.filter(t => t.tags.includes(options.tag));
        }

        return tests;
    }

    /**
     * 获取测试详情
     * @param {string} testPath - 测试路径
     */
    get(testPath) {
        const fullPath = path.join(this.testDir, testPath);
        if (!fs.existsSync(fullPath)) {
            return null;
        }

        const metadata = this._readMetadata();
        const meta = metadata.tests[testPath] || {};
        const content = fs.readFileSync(fullPath, 'utf-8');
        const stat = fs.statSync(fullPath);

        return {
            path: testPath,
            fullPath,
            content,
            metadata: {
                ...meta,
                createdAt: meta.createdAt || stat.birthtime.toISOString(),
                modifiedAt: stat.mtime.toISOString(),
                size: stat.size
            }
        };
    }

    /**
     * 创建新测试
     * @param {Object} testInfo - 测试信息
     */
    create(testInfo) {
        const { name, description, category = 'custom', content } = testInfo;

        const categoryDir = path.join(this.testDir, category);
        if (!fs.existsSync(categoryDir)) {
            fs.mkdirSync(categoryDir, { recursive: true });
        }

        const filename = `${name}.air.py`;
        const testPath = path.join(category, filename);
        const fullPath = path.join(this.testDir, testPath);

        // 写入文件
        fs.writeFileSync(fullPath, content, 'utf-8');

        // 更新元数据
        const metadata = this._readMetadata();
        metadata.tests[testPath] = {
            name,
            description,
            category,
            createdAt: new Date().toISOString(),
            tags: testInfo.tags || []
        };
        this._writeMetadata(metadata);

        return {
            success: true,
            path: testPath,
            fullPath
        };
    }

    /**
     * 根据描述生成并创建测试
     * @param {string} description - 测试描述
     * @param {Object} options - 生成选项
     */
    generate(description, options = {}) {
        const result = this.generator.generate(description, options);

        // 保存测试
        const testPath = path.relative(this.testDir, result.outputPath);
        const createResult = this.create({
            name: options.name || path.basename(result.outputPath, '.air.py'),
            description,
            category: result.category,
            content: result.code,
            tags: options.tags || []
        });

        return {
            ...createResult,
            steps: result.steps
        };
    }

    /**
     * 更新测试
     * @param {string} testPath - 测试路径
     * @param {Object} updates - 更新内容
     */
    update(testPath, updates) {
        const fullPath = path.join(this.testDir, testPath);
        if (!fs.existsSync(fullPath)) {
            return { success: false, error: '测试不存在' };
        }

        // 更新文件内容
        if (updates.content) {
            fs.writeFileSync(fullPath, updates.content, 'utf-8');
        }

        // 更新元数据
        const metadata = this._readMetadata();
        metadata.tests[testPath] = {
            ...metadata.tests[testPath],
            ...updates.metadata,
            updatedAt: new Date().toISOString()
        };
        this._writeMetadata(metadata);

        return { success: true, path: testPath };
    }

    /**
     * 删除测试
     * @param {string} testPath - 测试路径
     */
    delete(testPath) {
        const fullPath = path.join(this.testDir, testPath);
        if (!fs.existsSync(fullPath)) {
            return { success: false, error: '测试不存在' };
        }

        fs.unlinkSync(fullPath);

        // 更新元数据
        const metadata = this._readMetadata();
        delete metadata.tests[testPath];
        this._writeMetadata(metadata);

        return { success: true };
    }

    /**
     * 执行测试
     * @param {string} testPath - 测试路径
     * @param {Object} options - 执行选项
     */
    async run(testPath, options = {}) {
        const result = await this.runner.run(testPath, options);

        // 更新元数据
        const metadata = this._readMetadata();
        if (metadata.tests[testPath]) {
            metadata.tests[testPath].lastRun = result.startTime;
            metadata.tests[testPath].lastStatus = result.status;
            this._writeMetadata(metadata);
        }

        return result;
    }

    /**
     * 执行分类下所有测试
     * @param {string} category - 分类名称
     */
    async runCategory(category, options = {}) {
        const tests = this.list({ category });
        const results = [];

        for (const test of tests) {
            console.log(`Running: ${test.name}`);
            const result = await this.run(test.path, options);
            results.push(result);
        }

        return {
            category,
            total: tests.length,
            passed: results.filter(r => r.status === 'passed').length,
            failed: results.filter(r => r.status === 'failed').length,
            results
        };
    }

    /**
     * 获取历史报告
     * @param {string} testId - 测试ID
     */
    getReport(testId) {
        const reportPath = path.join(this.reportDir, 'html', `${testId}.html`);

        if (!fs.existsSync(reportPath)) {
            return null;
        }

        return {
            testId,
            path: reportPath,
            url: `file://${reportPath}`,
            content: fs.readFileSync(reportPath, 'utf-8')
        };
    }

    /**
     * 列出历史报告
     */
    listReports() {
        const reportsDir = path.join(this.reportDir, 'html');
        if (!fs.existsSync(reportsDir)) return [];

        const reports = [];
        const files = fs.readdirSync(reportsDir);

        files.forEach(file => {
            if (file.endsWith('.html')) {
                const testId = file.replace('.html', '');
                const stat = fs.statSync(path.join(reportsDir, file));

                reports.push({
                    testId,
                    path: file,
                    createdAt: stat.birthtime.toISOString(),
                    size: stat.size
                });
            }
        });

        return reports.sort((a, b) =>
            new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        );
    }

    /**
     * 统计信息
     */
    stats() {
        const tests = this.list();
        const reports = this.listReports();

        return {
            totalTests: tests.length,
            byCategory: tests.reduce((acc, t) => {
                acc[t.category] = (acc[t.category] || 0) + 1;
                return acc;
            }, {}),
            byStatus: tests.reduce((acc, t) => {
                const status = t.lastStatus || 'never_run';
                acc[status] = (acc[status] || 0) + 1;
                return acc;
            }, {}),
            totalReports: reports.length,
            lastReport: reports[0] || null
        };
    }
}

// 导出模块
module.exports = TestManager;

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    const manager = new TestManager();

    const handleCommand = async () => {
        switch (args[0]) {
            case 'list':
                console.log(JSON.stringify(manager.list(), null, 2));
                break;
            case 'get':
                console.log(JSON.stringify(manager.get(args[1]), null, 2));
                break;
            case 'stats':
                console.log(JSON.stringify(manager.stats(), null, 2));
                break;
            case 'run':
                console.log(JSON.stringify(await manager.run(args[1]), null, 2));
                break;
            case 'reports':
                console.log(JSON.stringify(manager.listReports(), null, 2));
                break;
            default:
                console.log('Commands: list, get <path>, stats, run <path>, reports');
        }
    };

    handleCommand().catch(console.error);
}
