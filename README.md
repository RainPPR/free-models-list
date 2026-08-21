# free-models-list

自动获取各平台免费模型列表，生成 [AI Math](https://github.com/RainPPR/ai-math-chat-studio) 配置文件。

每 8 小时自动更新一次（GitHub Actions）。

## Providers

| Provider | 脚本 | 输出 | 数据源 |
|----------|------|------|--------|
| Kilo | `kilo-free-ai-math.py` | `kilo-free-ai-math.json` | [api.kilo.ai](https://api.kilo.ai/api/gateway/models) |
| OpenCode | `opencode-free-ai-math.py` | `opencode-free-ai-math.json` | [opencode.ai](https://opencode.ai/zen/v1/models) |
| LogFare | `logfare-ai-math.py` | `logfare-ai-math.json` | [logfare.ai](https://logfare.ai/v1/models) |
| Poe | `poe-free-ai-math.py` | `poe-free-ai-math.json` | [api.poe.com](https://api.poe.com/v1/models) |

## 输出格式

```json
[
  {
    "id": "<uuid5>",
    "modelId": "<model_id>",
    "displayName": "<name> (<Provider>)",
    "reasoningEffort": "<effort>"
  }
]
```

其中 `reasoningEffort` 为可选字段。

## 项目结构

```
├── shared.py                     # 共用工具函数（UUID 生成）
├── kilo-free-ai-math.py          # Kilo provider
├── opencode-free-ai-math.py      # OpenCode provider
├── logfare-ai-math.py            # LogFare provider
├── poe-free-ai-math.py           # Poe provider
├── *.json                        # 各 provider 的输出文件
├── .github/workflows/
│   └── update-models.yml         # 自动更新 workflow
├── pyproject.toml
└── README.md
```

## 本地运行

```bash
uv sync
uv run python kilo-free-ai-math.py
uv run python opencode-free-ai-math.py
uv run python logfare-ai-math.py
uv run python poe-free-ai-math.py
```
