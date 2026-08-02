#!/usr/bin/env python3
"""
获取 opencode 模型列表并生成配置文件：
1. 从 https://opencode.ai/zen/v1 保存完整列表到 opencode.json
2. 将免费模型（id 以 -free 结尾）保存到 opencode-free.json
3. 从 https://models.dev/api.json 读取 opencode 项，合并 id 以 -free 结尾或 cost 全为 0 的模型，生成 opencode-free-ai-math.json
"""

import json
from pathlib import Path

import requests

from generate_kilo_ai_math_config import generate_model_uuid

BASE_DIR = Path(__file__).parent
OPENCODE_URL = "https://opencode.ai/zen/v1/models"
MODELS_DEV_URL = "https://models.dev/api.json"
API_KEY = "public"


def fetch_opencode_models() -> dict:
    """请求 opencode 模型列表。"""
    response = requests.get(OPENCODE_URL, headers={"Authorization": f"Bearer {API_KEY}"})
    response.raise_for_status()
    return response.json()


def fetch_models_dev_opencode() -> dict:
    """请求 models.dev API 并获取 opencode 的 models 字典。"""
    response = requests.get(MODELS_DEV_URL)
    response.raise_for_status()
    return response.json().get("opencode", {}).get("models", {})


def is_all_zero_cost(cost: dict | None) -> bool:
    """判断 cost 字典中的所有数值项是否均为 0。"""
    if not isinstance(cost, dict) or not cost:
        return False

    def check_values(d):
        for k, v in d.items():
            if isinstance(v, (int, float)):
                if v != 0:
                    return False
            elif isinstance(v, dict):
                if not check_values(v):
                    return False
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict) and not check_values(item):
                        return False
        return True

    return check_values(cost)


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

    # 3. 从 models.dev 生成 opencode-free-ai-math.json
    models_dev_opencode = fetch_models_dev_opencode()
    ai_math = []
    for m_id, model in models_dev_opencode.items():
        model_id = model.get("id", m_id)
        cost = model.get("cost")

        is_free_id = model_id.endswith("-free")
        is_free_cost = is_all_zero_cost(cost)

        if is_free_id or is_free_cost:
            name = model.get("name", model_id)
            config = {
                "id": generate_model_uuid(model_id),
                "modelId": model_id,
                "enableTools": True,
                "disabledTools": [],
                "displayName": f"{name} (OpenCode)",
            }

            reasoning_effort = get_reasoning_effort_from_models_dev(model)
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

