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