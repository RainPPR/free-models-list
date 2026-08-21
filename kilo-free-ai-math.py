#!/usr/bin/env python3
"""
获取 Kilo 免费模型列表，生成 AI Math 配置文件 kilo-free-ai-math.json。
"""

import json
from pathlib import Path

import requests

from shared import generate_model_uuid

BASE_DIR = Path(__file__).parent
API_URL = "https://api.kilo.ai/api/gateway/models"


def get_reasoning_effort(model: dict) -> str | None:
    """获取推理努力级别，按照 max -> high -> medium -> low 优先级。"""
    variants = model.get("opencode", {}).get("variants", {})
    if not variants:
        return None

    for effort in ("max", "xhigh", "high", "medium", "low", "minimal"):
        if effort in variants:
            return effort

    return None


def main() -> int:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    # 筛选 isFree 为 true 的模型并生成 AI Math 配置
    ai_math = []
    for model in data.get("data", []):
        if model.get("isFree") is not True:
            continue

        model_id = model.get("id", "")
        if not model_id:
            continue

        name = model.get("name", model_id)
        # 移除结尾的 " (free)" 后缀
        if name.endswith(" (free)"):
            name = name[:-7]

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "displayName": f"{name} (Kilo)",
        }

        reasoning_effort = get_reasoning_effort(model)
        if reasoning_effort:
            config["reasoningEffort"] = reasoning_effort

        ai_math.append(config)

    with open(BASE_DIR / "kilo-free-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(ai_math)} 个 Kilo 免费 AI Math 配置到 kilo-free-ai-math.json")
    return 0


if __name__ == "__main__":
    exit(main())
