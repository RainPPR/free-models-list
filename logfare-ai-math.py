#!/usr/bin/env python3
"""
获取 LogFare 模型列表，筛选支持文本生成的模型，生成 AI Math 配置文件 logfare-ai-math.json。

过滤逻辑：只保留 endpoints 包含 "chat/completions" 或 "responses" 的模型。
"""

import json
from pathlib import Path

import requests

from shared import generate_model_uuid

BASE_DIR = Path(__file__).parent
API_URL = "https://logfare.ai/v1/models"

# 满足任一即视为文本生成模型
TEXT_ENDPOINTS = {"chat/completions", "responses"}


def is_text_model(model: dict) -> bool:
    """判断模型是否支持文本生成（endpoints 包含 chat/completions 或 responses）。"""
    endpoints = model.get("endpoints", [])
    if not isinstance(endpoints, list):
        return False
    return bool(TEXT_ENDPOINTS & set(endpoints))


def main() -> int:
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    ai_math = []
    for model in data.get("data", []):
        if not is_text_model(model):
            continue

        model_id = model["id"]
        display_name = model.get("display_name", model_id)

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "displayName": f"{display_name} (LogFare)",
        }
        ai_math.append(config)

    with open(BASE_DIR / "logfare-ai-math.json", "w", encoding="utf-8") as f:
        json.dump(ai_math, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(ai_math)} 个 LogFare AI Math 配置到 logfare-ai-math.json")
    return 0


if __name__ == "__main__":
    exit(main())
