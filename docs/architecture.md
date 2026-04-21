# my-codeforces 系统架构设计文档 (v1.1)

## 1. 技术栈选型
- **后端 (Backend):** FastAPI (Python)
  - 理由：原生支持异步处理，方便调用子进程运行 Python 代码，且与刷题语言一致。
- **前端 (Frontend):** React + Tailwind CSS
  - 编辑器组件：Monaco Editor (VS Code 同款内核)。
  - 异步处理：利用 React Suspense 模式处理题目抓取状态。
- **通信:** RESTful API。

## 2. 数据存储设计 (Source of Truth)
系统采用“扁平化文件系统”存储方案，不依赖外部数据库。

### 2.1 目录结构与识别逻辑
```text
/
├── 800/
│   ├── 78A_v1.py        # 代码文件
│   ├── 78A_v2.py        
│   └── 78A.yaml         # 共享测试数据
├── 900/
└── docs/
```
- **版本识别：** 系统以文件名中第一个下划线 `_` 为界。
  - 示例：`78A_v1.py` -> 题号：`78A`，版本名：`v1`。
  - 示例：`112A.py` -> 题号：`112A`，版本名：`default`。
- **扫描器行为：** 扫描所有子目录（800, 900, 1000等）下的 `.py` 文件，按题号归组。

### 2.2 代码内嵌元数据 (Metadata)
代码文件头部必须包含特定的标签区域，用于系统识别：
```python
# === METADATA ===
# ProblemId: 78A
# Title: Help Far Away Kingdom
# Rating: 800
# Tags: strings, greedy
# Status: AC        # 可选值: TODO, AC, WA
# LastModified: 2026-04-19
# === END METADATA ===
```
- **存量升级 (Legacy Support):** 当打开无此标签的旧文件时，系统将根据文件名推断 ProblemId，联网获取 Title/Rating 后，在文件头部插入此标签块。

### 2.3 本地调试区 (Local Debug)
用于放置不想提交到 Codeforces 的代码（如本地测试逻辑）：
```python
# === LOCAL_DEBUG_START ===
# [本地测试代码]
# === LOCAL_DEBUG_END ===
```

### 2.4 测试数据格式 (YAML)
采用共享模式，题号相同的版本共用一个 YAML：
```yaml
samples:
  - input: |
      3
      abc
    expected_output: |
      YES
```

## 3. 核心模块设计

### 3.1 爬虫模块 (Scraper)
- **解析项:** Title, Rating, Tags, Sample Inputs/Outputs。
- **策略:** 异步请求，超时时间 5-10s。具备反爬感知，失败时返回标准错误码，引导用户手动录入。

### 3.2 评测引擎 (Runner)
- **隔离环境:** 在题目所在目录启动子进程。
- **环境探测:** 优先寻找项目根目录下的 `.venv`。
- **超时控制:** 默认设置 2s 强制超时。子进程超时后，后端负责销毁进程组并返回 `TLE`。
- **对比逻辑:** 极简对比（去除每行末尾空格 + 去除文件末尾所有空行）。
- **安全防护:** 限制 `stdout/stderr` 缓冲区大小（1MB）。

### 3.3 代码清洗器 (Cleaner)
- **逻辑:** 剔除 `# === LOCAL_DEBUG_START ===` 到 `# === LOCAL_DEBUG_END ===` 的内容，保留 `METADATA` 供参考。

### 3.4 现场恢复与自动暂存 (Persistence)
- **状态恢复:** 后端维护一个 `.config/last_session.json`（不入库），记录最后编辑的文件路径，支持 Resume 模式。
- **自动暂存:** 
  - 前端在 `onBlur`、切换版本、或窗口 `beforeunload` 时触发 `POST /api/save`。
  - 切换版本前必须先完成当前代码的暂存。

## 4. 接口 (API) 设计

### 4.1 题目管理
- `POST /api/init`: 初始化题目，触发爬虫。
- `POST /api/save`: 暂存/保存编辑器内容。
- `GET /api/history`: 扫描文件系统，解析 Metadata。返回结构包含题号及其关联的所有版本信息。

### 4.2 执行与评测
- `POST /api/run`: 调用子进程运行测试。
- `POST /api/mark-ac`: 修改代码文件中的 Metadata 状态。

## 5. 跨平台适配 (macOS)
- **容灾脚本:** 
  ```bash
  printf 'CODE_CONTENT' > /tmp/cf_run.py && python3 /tmp/cf_run.py
  ```
