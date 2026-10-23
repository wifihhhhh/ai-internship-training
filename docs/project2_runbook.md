# 项目二：带审核的学习简报助手——运行手册

核对日期：2026-10-22。本文依据当前仓库代码编写。

## 1. 项目用途与流程

输入学习主题，系统从本地知识库检索资料，由真实千问生成简报，经模型审查后等待人工决定。批准后导出 Markdown；拒绝则不导出。

```text
用户主题 → 检索 Agent → 写作 → 审查
                              ├─ 需修改且未修订 → 修订一次 → 再审查
                              ├─ 依据不足或仍不合格 → 人工修改状态，结束
                              └─ 通过 → 等待人工审批
                                         ├─ 批准 → 校验并导出
                                         └─ 拒绝 → 结束，不导出
```

- 检索：最多 3 次工具搜索，每次取 2 块，最多收集 6 个不同片段；节点重试时可能重新搜索。
- 写作：只能依据提供的原文生成简报，程序校验引用 ID 和逐字引文。
- 审查：另一轮模型调用检查事实依据；审查通过不代表绝对正确。
- 修订：最多一次内容修订，与临时错误重试是不同机制。
- 审批：用户批准具体内容摘要后，程序才能进入导出节点。

这是单用户、本机演示项目。服务同步处理请求，使用进程内全局锁串行执行。

## 2. 目录与职责

项目根目录：`C:\Users\Tina\Documents\ai-internship-training`。

| 路径（相对项目根目录） | 用途 |
| --- | --- |
| `src/report_lab/server.py` | 独立 FastAPI 服务与令牌认证 |
| `src/report_lab/graph.py` | 角色协调、条件分支与修订限制 |
| `src/report_lab/researcher.py` | 受限知识库搜索工具与检索 Agent |
| `src/report_lab/writer.py`、`reviewer.py` | 真实千问写作与审查 |
| `src/report_lab/helpers.py` | JSON 解析、引用校验 |
| `src/report_lab/approval.py` | 中断审批、审批后导出 |
| `src/report_lab/export.py` | 报告渲染、内容摘要、幂等文件写入 |
| `src/report_lab/persistence.py` | SQLite Checkpoint 生命周期 |
| `src/rag_lab/` | 复用文档处理、向量模型和 Chroma 检索 |
| `src/langchain_lab/models.py` | 复用真实千问聊天客户端 |
| `knowledge/` | 原始 Markdown 学习笔记 |
| `report_frontend/index.html` | 新项目审批页面；与旧 `frontend/` 分开 |
| `data/chroma/` | 本地向量索引 |
| `data/report_checkpoints.sqlite` | 持久化任务、资料片段、草稿和审批状态 |
| `exports/` | 批准后生成的 Markdown |
| `data/evaluations/` | Day 81 原始评估与人工评分 |

项目二的 `/tasks` 是“报告任务”。它与旧 8000 服务的同名任务管理接口含义不同。

## 3. 环境与依赖

当前使用 Windows PowerShell、Python 3.12.4。以下命令均从项目根目录执行。

```powershell
cd C:\Users\Tina\Documents\ai-internship-training
.\.venv\Scripts\Activate.ps1
```

已有环境先检查依赖，不需要每次重装：

```powershell
python -m pip check
```

新环境可先创建虚拟环境、安装仓库已有基础依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

注意：当前 `requirements.txt` 还是前期快照，没有完整列出后续 AI 依赖。下列版本来自核对日的已安装环境；新环境还需补充：

```powershell
python -m pip install "langchain==1.4.4" "langchain-core==1.6.9" "langchain-openai==1.7.0" "langchain-chroma==1.1.0" "langchain-text-splitters==1.1.3" "langgraph==1.2.14" "langgraph-checkpoint-sqlite==3.1.2" "openai==3.29.0"
python -m pip check
```

这些版本在现有环境中已核对；尚未在全新环境执行完整重装验证。项目二入口不依赖旧服务的 MySQL、Redis 启动，但需要本地 Chroma 索引和百炼网络访问。

## 4. 环境变量

在根目录 `.env` 中追加或更新配置，保留原有数据库等配置。下面没有任何真实密钥。

```dotenv
DASHSCOPE_API_KEY=替换为真实百炼密钥
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=替换为该密钥所属地域和业务空间的兼容接口BaseURL
QWEN_EMBED_MODEL=text-embedding-v4
QWEN_EMBED_DIMENSIONS=1024
RAG_COLLECTION=learning_notes_v1
REPORT_API_TOKEN=替换为至少24字符的随机本地访问令牌
```

`QWEN_EMBED_BASE_URL` 可选；未配置时向量模型复用 `QWEN_BASE_URL`。已有调用成功的地址应继续使用，不要把示例占位文字当成地址。

两种令牌用途不同：

- `DASHSCOPE_API_KEY`：后端连接百炼，不能填进网页访问令牌框。
- `REPORT_API_TOKEN`：本地页面及 API 的访问认证，服务启动时要求至少 24 字符。

可在自己终端中生成本地随机令牌，将输出粘贴到 `.env`：

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

不要分享输出。修改 `.env` 后重启服务；客户端和令牌可能已被缓存。

## 5. 准备知识库

1. 把非空、UTF-8 编码的 Markdown 文件放到根目录 `knowledge/`。
2. 检查加载和切块：

```powershell
python -m scripts.day44_chunks_demo
```

3. 首次导入：

```powershell
python -m scripts.day46_ingest
```

4. 修改已有非空文件后同步：

```powershell
python -m scripts.day51_sync_knowledge
```

5. 验证检索：

```powershell
python -m scripts.day47_retrieve_demo
```

导入和查询向量会调用真实服务。重复导入会跳过已存在的片段，但换向量模型、维度或切块方案时，应换集合并重新建立索引。

当前同步脚本只同步读取到的非空文件：删除或清空整个文件不会自动完整清理旧片段；新增和删除也不是一个事务。不要把该机制描述为生产级文档同步。

## 6. 启动服务与页面

```powershell
python -m uvicorn src.report_lab.server:app --host 127.0.0.1 --port 8001
```

- 页面：<http://127.0.0.1:8001/ui/>
- API 文档：<http://127.0.0.1:8001/docs>
- OpenAPI：<http://127.0.0.1:8001/openapi.json>

终端显示服务启动后会保持运行，这是正常状态。不要关闭终端再操作页面。停止服务按 `Ctrl+C`。

本项目没有单独的 `/health` 接口。页面能打开只证明静态文件服务可达，不能证明模型与知识库已经可用。

只修改 HTML 后保存并 `Ctrl+F5` 强制刷新；修改 Python 后，按上述非热重载启动命令运行的服务需要重启。

## 7. 页面操作

1. 打开 `/ui/`，输入 `REPORT_API_TOKEN`，不要输入百炼密钥。
2. 填写主题，例如“根据学习笔记，整理 Redis 缓存失效简报”。
3. 点击“生成简报”，等待检索、写作、审查完成。
4. 等待期间会进行多次真实请求；新请求还可能等待当前任务释放全局锁。
5. 状态为 `awaiting_approval` 时，逐字检查预览和引用。
6. 点击“批准导出”后状态应为 `exported`，此时可以下载。
7. 点击“拒绝”后为 `rejected`，不能下载。

若为 `needs_manual_revision`，说明依据不足或有限修订后仍未通过，不会进入审批。当前页面没有“编辑后继续”入口，需要改善资料或问题，再新建任务。

页面刷新会清空浏览器内的当前任务对象和输入令牌，但不会删除 SQLite 中的任务。请记下任务 ID，可从 `/docs` 查询旧任务。

## 8. API 操作

四个接口均要求认证。`/docs` 点击 **Authorize**，在 HTTP Bearer 输入框填写本地访问令牌本身，不要重复添加 `Bearer `。

通过代码调用时，请求头应为：

```text
Authorization: Bearer <REPORT_API_TOKEN>
```

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| POST | `/tasks` | 同步生成报告，直到等待审批或正常停止 |
| GET | `/tasks/{task_id}` | 查询草稿、审查和等待审批信息 |
| POST | `/tasks/{task_id}/decision` | 批准或拒绝当前确定的报告 |
| GET | `/tasks/{task_id}/download` | 下载已批准导出的文件 |

创建请求：

```json
{"question": "根据学习笔记，整理Redis缓存失效简报。"}
```

保存响应的 `task_id`，查看 `status`、`draft`、`review`、`approval.preview` 和 `approval.digest`。

当前服务返回紧凑 UUID，`/docs` 的 UUID 输入校验可能要求连字符形式。转换示例：

```powershell
python -c "from uuid import UUID; print(str(UUID('9fc53f99bc0e4d4c8915f12c8ffe067a')))"
```

该例输出 `9fc53f99-bc0e-4d4c-8915-f12c8ffe067a`。实际操作替换为自己的任务 ID；两种形式表示同一 UUID，后端使用 `.hex` 查状态。

审批接口的 `task_id` 填上方路径输入框，请求体填写：

```json
{
  "approved": true,
  "digest": "替换为当前任务approval.digest中的64位摘要"
}
```

拒绝时使用 `false`，摘要仍取当前任务真实值。不要把占位文字直接提交。

- `awaiting_approval`：模型审查通过，仍未批准或导出。
- `exported`：人工批准且文件写入成功，可以下载。
- `rejected`：人工拒绝，不能下载。
- `needs_manual_revision`：资料不足或模型审查最终未通过。
- `failed`：查询状态时检测到图任务异常，需要排查；不是正常拒答。

同一已完成任务重复审批返回 409。内容摘要不匹配也返回 409，避免批准的内容与导出内容不同。

当前接口没有 Pydantic 响应模型，OpenAPI 的成功响应示例可能显示 `"string"`，实际返回字典 JSON；不能以该示例判断真实响应结构。

## 9. 恢复等待审批的任务

服务重启后继续使用同一个任务 ID，通过 GET 查询，再提交当前审批摘要。也可运行：

```powershell
python -m scripts.day76_resume_report
```

输入已有任务 ID，检查打印的预览；输入 `yes` 批准，其他输入拒绝。建议运行 CLI 恢复前先停掉 Web 服务，避免两个进程操作同一任务。

恢复依赖根目录下 `data/report_checkpoints.sqlite`。不要删除该文件；删除会失去任务状态。更新工作流节点与状态结构后，旧任务不保证兼容，验证新版流程请创建新任务。

该脚本只处理已经等待审批的任务，不是所有失败节点的自动恢复工具。发生故障后先定位，不要反复 POST 创建相同主题并产生额外费用。

## 10. 文件导出与幂等边界

批准后默认生成：

```text
exports/<任务UUID紧凑形式>-<内容摘要前12位>.md
```

相同任务、相同内容重复调用导出函数会复用已有文件；文件名由 UUID 与内容摘要生成，不能由请求指定任意路径。

先写临时文件，再替换到目标文件，以减少半截报告。它不是分布式锁或跨文件与数据库的事务，也不能宣称“分布式恰好一次”。如果文件已经写入但状态提交失败，需要排查 Checkpoint 和文件现状。

## 11. 自动测试

从根目录运行：

```powershell
python -m pytest tests/test_report_evidence.py tests/test_report_export.py tests/test_report_retry.py -q
```

当前 7 个用例覆盖引用真实性、未知来源、重复导出、非法任务 ID，以及部分不可重试错误。它们不调用真实模型，也不代表所有 API 和审批场景都已自动覆盖。

2026-10-22 实测：`7 passed`，退出码为 0。首次执行时断言通过但旧 pytest 临时目录清理遇到 WinError 5；换独立临时目录后正常退出。遇到类似环境问题，可使用一个尚不存在的新路径：

```powershell
python -m pytest tests/test_report_evidence.py tests/test_report_export.py tests/test_report_retry.py -q -p no:cacheprovider --basetemp data/pytest-day83-new-run
```

注意：pytest 可能清理指定 basetemp。每次选专用新目录，不要把它设为 `data`、项目根目录或已有业务目录。不要通过删除整片临时目录来处理权限错误。

## 12. 真实效果评估

先跑一个问题：

```powershell
python -m scripts.day81_evaluate --limit 1
```

需要扩大样本时：

```powershell
python -m scripts.day81_evaluate --limit 10
```

每次生成独立目录，保存 `results.jsonl`、`review.md` 和 `scores.csv`。脚本使用内存 Checkpoint，在审批前停止；不会批准或触发报告业务导出，但会调用真实聊天及向量服务并产生费用。

人工评分不能直接采用模型 `review.passed`。需对照资料检查 task、grounding、citations、clarity。通过规则：前三项均为 2，clarity 至少 1，并且执行没有错误。

现有记录：[2026-10-22 原始结果](../data/evaluations/day81_20261022_132312_283a8d/results.jsonl)、[人工评分](../data/evaluations/day81_20261022_132312_283a8d/scores.csv)。

| 指标，仅 C01 | single | multi |
| --- | --- | --- |
| 人工评分 | 2 / 1 / 1 / 2 | 2 / 1 / 1 / 2 |
| 严格通过 | 否 | 否 |
| 耗时 | 11.20 秒 | 19.54 秒 |
| 观察到的模型启动次数 | 1 | 6 |
| 收集到的总 Token | 1,335 | 6,783 |

两份正文相同，都把“不能只依赖缓存”扩大为持久化能力方面的断言；模型审查未发现问题。只能说本条样例没有观察到多角色收益，不能据一个问题推广整体结论。用量回调不包含完整 Embedding 账单，也不保证覆盖失败请求的全部费用。

待办：[week12_eval.md](week12_eval.md) 当前为空，尚需整理更大样本的评估结论；`scripts/day81_summarize.py` 当前也为空，运行不会产生统计。不要把单问题记录描述成已完成 10 题评估。

## 13. 常见故障定位

| 表现 | 检查方法 |
| --- | --- |
| 页面无法连接 | 确认服务终端仍运行，地址为 8001，检查端口占用 |
| 点击后没有等待文字，按钮变灰 | 浏览器 F12 Console 检查 DOM 选择器拼写和 JS 异常；再看 Network 是否真的发送请求 |
| 一直等待 | 当前是同步多轮模型请求，也可能等待全局锁；不要重复点击，查看终端和 Network |
| 401 | 本地令牌、`Bearer ` 后空格、服务是否重启、是否错填百炼密钥 |
| 422 / Guid 校验失败 | 空白或超长主题；`task_id` 放路径框并使用连字符 UUID；审批摘要必须为真实64位十六进制字符串 |
| `{"detail":"Not Found"}` | 核对端口和 `/tasks/.../download` 拼写，特别是 `tasks`，强制刷新旧页面 |
| 404 任务不存在 | 核对任务ID和 Checkpoint 文件；不是创建新任务来替代查询 |
| 409 | 状态不允许审批/下载，或摘要不匹配；先 GET 查当前状态 |
| 502 | 查看终端 `task_id` 与错误类型，可能是百炼、引用校验、图执行或导出错误；502 不必然是网络错误 |
| 知识库没有文档 | 检查 `knowledge/*.md`，加载通配符应为 `*.md`，运行切块和导入脚本 |
| 未知图目标 | 条件映射必须指向已注册节点，审查通过应进入 `approve`，不是旧 `finish` |
| 修改Python后仍旧行为 | 按本文启动命令没有启用热重载，需停服重启 |

现有服务器错误日志主要记录任务 ID 与异常类型，不包含完整 traceback。若仍不能定位，可在本地单独运行对应 CLI 查看详细异常；不要把带密钥或个人资料的完整日志公开。

## 14. 数据保护与已知限制

- `.env`、Checkpoint、向量库、导出文件、原始评估内容可能包含私有信息。
- 当前 `.gitignore` 已忽略 `.env`，但 `data/*.db` 不覆盖 `.sqlite`、Chroma 子目录、评估结果或 `exports/`；提交前必须用 `git status` 检查并完善忽略规则，已跟踪文件不会因新增规则自动取消跟踪。
- 不自动删除数据库、向量库或报告；清理和备份应确认具体对象。
- 单一共享令牌没有用户账号、角色授权或会话所有权隔离；持有令牌者可操作可知的任务ID。
- 同步接口、全局锁和 SQLite 是本地训练设计，不支持生产级后台队列、分布式协调与高并发。
- 搜索次数限制按研究节点的一次执行计算；外层节点重试会重置计数，向量客户端也有内部重试，不能据此推算整任务精确费用上限。
- 模型审查可能漏错，逐字引用校验不证明全部语义；无依据任务可能无法完成。
- 页面令牌保存在当前页面内存，草稿以文本显示；刷新后的旧任务恢复需使用 API 文档或 CLI。
- 当前 API 未实现报告编辑、失败任务专用重试入口、完整审计日志、任务取消与自动数据保留策略。

## 15. Day 84 演示顺序

1. 展示知识文件和检索结果。
2. 创建任务，解释检索、写作、审查与一次修订。
3. 检查草稿、引用和审批摘要。
4. 批准并下载；另建任务展示拒绝后不能下载。
5. 用同一任务ID展示停服后恢复等待审批。
6. 展示 7 个本地规则测试与真实评估的区别。
7. 用单条真实失败案例说明模型审查的局限，说明尚未完成的能力。
