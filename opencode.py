#!/usr/bin/env python3
"""
获取 opencode 模型列表并生成配置文件：
1. 从 https://opencode.ai/zen/v1 保存完整列表到 opencode.json
2. 将免费模型（id 以 -free 结尾）保存到 opencode-free.json
3. 生成 opencode-free-ai-math.json（基于 opencode-free.json 免费模型列表，从 models.dev 查找 displayName 名称）
"""

import json
from pathlib import Path

import requests

from generate_kilo_ai_math_config import generate_model_uuid

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


def fetch_opencode_models() -> dict:
    """请求 opencode 模型列表。"""
    response = requests.get(OPENCODE_URL, headers={"Authorization": f"Bearer {API_KEY}"})
    response.raise_for_status()
    return response.json()


def fetch_models_dev_opencode() -> dict:
    """请求 models.dev API 并获取 opencode 的 models 字典。"""
    try:
        response = requests.get(MODELS_DEV_URL)
        response.raise_for_status()
        return response.json().get("opencode", {}).get("models", {})
    except Exception:
        return {}


def get_reasoning_effort_from_models_dev(model: dict) -> str | None:
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

    priority_order = ["max", "high", "medium", "low"]
    for effort in priority_order:
        if effort in effort_values:
            return effort

    return None


def main() -> int:
    data = fetch_opencode_models()

    # 统一 created 字段为 0（UTC 1970-01-01 00:00:00）
    for model in data.get("data", []):
        if "created" in model:
            model["created"] = 0

    # 1. 保存完整列表到 opencode.json
    with open(BASE_DIR / "opencode.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # 2. 筛选免费模型（id 以 -free 结尾），保留原文保存到 opencode-free.json
    free_models = []
    for model in data.get("data", []):
        model_id = model.get("id", "")
        if model_id.endswith("-free"):
            free_models.append(dict(model))

    with open(BASE_DIR / "opencode-free.json", "w", encoding="utf-8") as f:
        json.dump(free_models, f, indent=4, ensure_ascii=False)

    # 3. 基于免费模型列表生成 opencode-free-ai-math.json（从 models.dev 查找名称）
    models_dev_opencode = fetch_models_dev_opencode()
    ai_math = []
    for model in free_models:
        model_id = model["id"]
        dev_model = models_dev_opencode.get(model_id, {})
        name = dev_model.get("name") or derive_name(model_id)

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "enableTools": True,
            "disabledTools": [],
            "displayName": f"{name} (OpenCode)",
        }

        reasoning_effort = get_reasoning_effort_from_models_dev(dev_model)
        if reasoning_effort:
            config["reasoningEffort"] = reasoning_effort

        ai_math.append(config)

    with open(BASE_DIR / "opencode-free-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(data.get('data', []))} 个模型到 opencode.json")
    print(f"已保存 {len(free_models)} 个免费模型到 opencode-free.json")
    print(f"已生成 {len(ai_math)} 个 AI Math 配置到 opencode-free-ai-math.json")

    return 0


if __name__ == "__main__":
    exit(main())


