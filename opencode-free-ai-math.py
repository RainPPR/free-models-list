#!/usr/bin/env python3
"""
获取 OpenCode 免费模型列表，生成 AI Math 配置文件 opencode-free-ai-math.json。
"""

import json
from pathlib import Path

import requests

from shared import generate_model_uuid

BASE_DIR = Path(__file__).parent
OPENCODE_URL = "https://opencode.ai/zen/v1/models"
MODELS_DEV_URL = "https://models.dev/api.json"
API_KEY = "public"


def derive_name(model_id: str) -> str:
    """根据模型 id 推导一个可读名称（移除 -free 后缀并做标题化）。"""
    name = model_id
    if name.endswith("-free"):
        name = name[:-5]
    return name.replace("-", " ").replace(":", " ").title()


def fetch_models_dev_opencode() -> dict:
    """请求 models.dev API 并获取 opencode 的 models 字典。"""
    try:
        response = requests.get(MODELS_DEV_URL, timeout=30)
        response.raise_for_status()
        return response.json().get("opencode", {}).get("models", {})
    except Exception:
        return {}


def get_reasoning_effort(model: dict) -> str | None:
    """从 models.dev 的 reasoning_options 中按 max -> high -> medium -> low 提取推理级别。"""
    options = model.get("reasoning_options", [])
    if not isinstance(options, list):
        return None

    effort_values = set()
    for opt in options:
        if isinstance(opt, dict) and opt.get("type") == "effort":
            vals = opt.get("values", [])
            if isinstance(vals, list):
                effort_values.update(vals)

    for effort in ("max", "xhigh", "high", "medium", "low", "minimal"):
        if effort in effort_values:
            return effort

    return None


def main() -> int:
    # 获取 OpenCode 模型列表
    response = requests.get(OPENCODE_URL, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=30)
    response.raise_for_status()
    data = response.json()

    # 筛选免费模型（id 以 -free 结尾）
    free_models = [m for m in data.get("data", []) if m.get("id", "").endswith("-free")]

    # 从 models.dev 获取名称和 reasoningEffort
    models_dev = fetch_models_dev_opencode()

    ai_math = []
    for model in free_models:
        model_id = model["id"]
        dev_model = models_dev.get(model_id, {})
        name = dev_model.get("name") or derive_name(model_id)

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "displayName": f"{name} (OpenCode)",
        }

        reasoning_effort = get_reasoning_effort(dev_model)
        if reasoning_effort:
            config["reasoningEffort"] = reasoning_effort

        ai_math.append(config)

    with open(BASE_DIR / "opencode-free-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(ai_math)} 个 OpenCode 免费 AI Math 配置到 opencode-free-ai-math.json")
    return 0


if __name__ == "__main__":
    exit(main())
