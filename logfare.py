#!/usr/bin/env python3
"""
获取 logfare 模型列表 (https://logfare.ai/v1/models)，并完成两件事：
1. 将完整列表原文保存到 logfare.json
2. 生成 logfare-ai-math.json（格式与 kilo-free-ai-math.json 相同，所有模型免费）
"""

import json
from pathlib import Path

import requests

from generate_kilo_ai_math_config import generate_model_uuid

BASE_DIR = Path(__file__).parent
URL = "https://logfare.ai/v1/models"


def main() -> int:
    response = requests.get(URL)
    response.raise_for_status()
    raw = response.json()

    # 统一 created 字段为 0（UTC 1970-01-01 00:00:00）
    for model in raw.get("data", []):
        if "created" in model:
            model["created"] = 0

    # 1. 原文保存到 logfare.json
    with open(BASE_DIR / "logfare.json", "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=4, ensure_ascii=False)

    # 2. 生成 logfare-ai-math.json
    ai_math = []
    for model in raw.get("data", []):
        model_id = model["id"]
        display_name = model.get("display_name", model_id)
        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "enableTools": True,
            "disabledTools": [],
            "displayName": f"{display_name} (LogFare)",
        }
        ai_math.append(config)

    with open(BASE_DIR / "logfare-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(raw.get('data', []))} 个模型到 logfare.json")
    print(f"已生成 {len(ai_math)} 个 AI Math 配置到 logfare-ai-math.json")

    return 0


if __name__ == "__main__":
    exit(main())
