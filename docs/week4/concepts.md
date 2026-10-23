# Prompt Lab 概念

## System Prompt

定义模型身份、任务、输出规则和安全边界。

## User Prompt

用户实际输入的问题或指令。

## Temperature

控制随机性。提取、分类、工具调用等任务通常使用较低值。

## Structured Output

要求模型返回固定 JSON 结构，再用 Pydantic 校验。

## Hallucination

模型输出看似合理、实际却不可靠的内容。

## Prompt Injection

用户输入尝试覆盖系统规则，例如要求模型忽略原有指令。