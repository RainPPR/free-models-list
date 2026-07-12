# free-models-list

## 项目概述

自动抓取多个 AI 平台的免费模型列表，生成结构化 JSON 供下游使用（如 AI Math 配置）。

## 数据源与脚本

| 脚本 | API 地址 | 生成文件 | 认证 |
|------|----------|----------|------|
| `main.py` | `https://api.kilo.ai/api/gateway/models` | `kilo.json`（全部，移除冗余字段）、`kilo-free.json`（免费，移除 isFree/pricing） | 无 |
| `opencode.py` | `https://opencode.ai/zen/v1/models` | `opencode.json`（全部）、`opencode-free.json`（id 以 `-free` 结尾）、`opencode-free-ai-math.json` | `Authorization: Bearer public` |
| `logfare.py` | `https://logfare.ai/v1/models` | `logfare.json`（全部）、`logfare-ai-math.json`（全部为免费） | 无 |

## 共享工具库

`generate_kilo_ai_math_config.py` 提供供所有脚本复用的核心函数：

- `generate_model_uuid(model_id: str) -> str` —— 基于 uuid5（DNS 命名空间）生成确定性 UUID，相同 modelId 永远输出相同 UUID
- `get_reasoning_effort(model: dict) -> str | None` —— 从模型 `opencode.variants` 按优先级提取推理级别：max > high > medium > low
- `generate_ai_math_config(models: list[dict]) -> list[dict]` —— 读取模型列表生成 ai-math 配置

### ai-math JSON 格式

```json
{
  "id": "5ab7cacf-75df-5490-8295-8edd9c1d374b",
  "modelId": "deepseek-v4-flash",
  "enableTools": true,
  "disabledTools": [],
  "displayName": "DeepSeek V4 Flash (LogFare)",
  "reasoningEffort": "high"   // 可选，仅有 variants 时出现
}
```

- `id`：必须使用 `generate_model_uuid(modelId)` 生成
- `displayName`：格式为 `"{可读名称} ({Provider})"`，Provider 值：`Kilo`、`OpenCode`、`LogFare`

## GitHub Actions

`.github/workflows/update-models.yml`

- 触发方式：每周一 UTC 00:00 自动执行 + `workflow_dispatch` 手动触发 + push 触发
- 执行顺序：`main.py` → `generate_kilo_ai_math_config.py` → `opencode.py` → `logfare.py`
- 所有 .json 产物均提交到仓库（`kilo.json`、`kilo-free.json`、`kilo-free-ai-math.json`、`opencode.json`、`opencode-free.json`、`opencode-free-ai-math.json`、`logfare.json`、`logfare-ai-math.json`）

## 技术栈

- Python ≥ 3.14
- 包管理：uv
- 依赖：`requests>=2.32.5`

## 运行方式

```bash
uv sync
uv run python main.py
uv run python generate_kilo_ai_math_config.py
uv run python opencode.py
uv run python logfare.py
```

## 新增/修改时的注意事项

1. 新增 API 源时：创建独立 .py，引入 `generate_kilo_ai_math_config` 的 `generate_model_uuid`；ai-math 的 `id` 必须用 `generate_model_uuid` 生成，不要自行实现 UUID 逻辑
2. 修改输出格式时：保持 `enableTools: true`、`disabledTools: []`、`displayName` 遵循 `"{name} ({Provider})"` 约定
3. 修改 `generate_kilo_ai_math_config.py` 时：确保向后兼容，其他脚本均依赖它的导出函数
4. 更新 GitHub Actions：如果新增/删除输出文件，必须同步更新 `git add` 和 `git commit` 部分的文件列表
5. 所有 .json 文件（现在用的是 `git add .` 而不是具体的 json 方便新增）由 CI 自动生成并提交，**禁止手动编辑**

## 重要规则

**任何对项目（脚本、工作流、配置文件、输出格式等）的修改，都必须同步更新本 AGENTS.md 文件。**
