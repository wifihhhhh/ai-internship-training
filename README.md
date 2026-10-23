# AI Internship Training

面向 AI 应用开发实习的工程化训练仓库。

## 当前进度

- Day 1：Python 虚拟环境、pytest、Git 初始化
- Day 3：任务数据模型
- Day 4：环境配置、日志与自定义异常
- Day 6：Git 分支、合并与冲突解决

## 当前功能

- `health()` 健康检查
- `Task` 任务模型
- `.env` 环境配置读取
- 结构化日志
- 任务不存在时抛出 `TaskNotFoundError`
- 标题标准化规则
- pytest 单元测试

## 项目结构

```text
src/       应用代码
tests/     自动化测试
.env.example  配置模板
```

## 本地运行

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m src.main
```

## 安全说明

`.env` 仅供本地使用，不会提交到 Git。真实 API Key、密码和数据库连接信息不得上传到 GitHub。

## 项目二：带审核的学习简报助手（Day 64–84）

基于真实千问、Chroma 与 LangGraph，编排检索 Agent、写作和审查角色；最多修订一次，人工批准具体内容后导出 Markdown。SQLite Checkpoint 支持跨进程恢复等待审批的任务。

- [完整运行手册：安装、配置、知识库、接口、审批、恢复和故障排查](docs/project2_runbook.md)
- [角色职责说明](docs/week10_roles.md)
- [安全测试记录](docs/week11_security.md)
- [Day 81 原始结果：目前只有 C01 的两种方案](data/evaluations/day81_20261022_132312_283a8d/results.jsonl)
- [Day 81 人工评分](data/evaluations/day81_20261022_132312_283a8d/scores.csv)
- [评估总结文件](docs/week12_eval.md)：当前为空，待补充完整评估。

### 快速启动

以下命令在项目根目录执行。先按运行手册补齐 AI 依赖和 `.env`：百炼密钥、匹配地域的模型地址、向量模型配置，以及至少 24 字符的本地 `REPORT_API_TOKEN`。当前 `requirements.txt` 尚未完整包含新增的 AI 依赖。

```powershell
cd C:\Users\Tina\Documents\ai-internship-training
.\.venv\Scripts\Activate.ps1
python -m scripts.day46_ingest
python -m uvicorn src.report_lab.server:app --host 127.0.0.1 --port 8001
```

已有索引且资料未变时，不必每次重新导入。真实向量与聊天调用会消耗百炼额度。

- [报告审批页面](http://127.0.0.1:8001/ui/)
- [报告 API 文档](http://127.0.0.1:8001/docs)

网页和 `/docs` 使用本地 `REPORT_API_TOKEN`，不是百炼密钥。生成后检查预览，批准才允许下载；服务终端需要保持运行。旧 8000 服务的 `/tasks` 为任务管理，本项目 8001 的 `/tasks` 为报告任务。

### 测试与恢复

```powershell
python -m pytest tests/test_report_evidence.py tests/test_report_export.py tests/test_report_retry.py -q
python -m scripts.day76_resume_report
```

2026-10-22 已验证 7 个本地规则测试通过；使用独立临时目录规避了旧 pytest 临时目录清理的权限错误。测试不调用真实模型，不能代替模型效果评估或 API 完整验收。

### 当前评估与边界

现有 C01 中，两种方案正文相同，人工评分均为 `2/1/1/2`，都未满足严格通过规则。多角色耗时 19.54 秒，简单方案 11.20 秒；本条没有观察到质量提升，不能推广为整体结论。

这是单用户本机演示：共享令牌、同步请求、全局锁、SQLite Checkpoint，无后台任务队列或多用户会话授权。模型审查可能漏错，引用校验不能证明全部结论。当前忽略规则未完整覆盖 `.sqlite`、向量库、导出和评估产物，提交前须检查 `git status`，不要上传私有运行数据。

上方 Day 1–6 内容保留为早期训练记录；实际 Web 服务请使用对应项目入口，`python -m src.main` 不等同于启动当前 FastAPI 服务。
