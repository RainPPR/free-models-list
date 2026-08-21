#!/usr/bin/env python3
"""
获取 Poe API 的免费模型列表，生成 AI Math 配置文件 poe-free-ai-math.json。

迁移自 https://github.com/RainPPR/poe-free-models
"""

import json
from pathlib import Path

import requests

from shared import generate_model_uuid

BASE_DIR = Path(__file__).parent
API_URL = "https://api.poe.com/v1/models"


def is_strictly_free(pricing: dict | None) -> bool:
    """检查价格是否严格为 0（免费）。"""
    if pricing is None or not isinstance(pricing, dict):
        return False

    has_any_price = False
    for key, value in pricing.items():
        if value is None:
            continue
        has_any_price = True
        try:
            if float(value) != 0:
                return False
        except (ValueError, TypeError):
            return False

    return has_any_price


def extract_reasoning_effort(model: dict) -> str | None:
    """从模型的 parameters 中提取 reasoning_effort 参数值。"""
    parameters = model.get("parameters")
    if not isinstance(parameters, list):
        return None

    for param in parameters:
        if isinstance(param, dict) and param.get("name") == "reasoning_effort":
            schema = param.get("schema")
            if (
                isinstance(schema, dict)
                and "enum" in schema
                and isinstance(schema["enum"], list)
                and len(schema["enum"]) > 0
            ):
                return str(schema["enum"][-1])
            if "default_value" in param and param["default_value"] is not None:
                return str(param["default_value"])

    return None


def main() -> int:
    print("正在获取 Poe 模型列表...")
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    models = response.json().get("data", [])
    print(f"获取到 {len(models)} 个模型")

    ai_math = []
    for model in models:
        if not is_strictly_free(model.get("pricing")):
            continue

        model_id = model.get("id", "")
        if not model_id:
            continue

        metadata = model.get("metadata", {})
        display_name = metadata.get("display_name", model_id)

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "displayName": f"{display_name} (Poe)",
        }

        reasoning_effort = extract_reasoning_effort(model)
        if reasoning_effort is not None:
            config["reasoningEffort"] = reasoning_effort

        ai_math.append(config)

    with open(BASE_DIR / "poe-free-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(ai_math)} 个 Poe 免费 AI Math 配置到 poe-free-ai-math.json")
    return 0


if __name__ == "__main__":
    exit(main())
