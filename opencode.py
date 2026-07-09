#!/usr/bin/env python3
"""
获取 opencode 模型列表 (https://opencode.ai/zen/v1)，并完成三件事：
1. 将完整列表保存为 opencode.json
2. 将免费模型（id 以 -free 结尾）保存为 opencode-free.json
3. 生成 opencode-free-ai-math.json（格式与 kilo-free-ai-math.json 相同）
"""

import json
from pathlib import Path

import requests

from generate_kilo_ai_math_config import generate_model_uuid, get_reasoning_effort

BASE_DIR = Path(__file__).parent
URL = "https://opencode.ai/zen/v1/models"
API_KEY = "public"


def derive_name(model_id: str) -> str:
    """根据模型 id 推导一个可读名称（移除 -free 后缀并做标题化）。"""
    name = model_id
    if name.endswith("-free"):
        name = name[: -len("-free")]
    return name.replace("-", " ").replace(":", " ").title()


def fetch_models() -> dict:
    """请求 opencode 模型列表。"""
    response = requests.get(URL, headers={"Authorization": f"Bearer {API_KEY}"})
    response.raise_for_status()
    return response.json()


def main() -> int:
    data = fetch_models()

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

    # 3. 生成 opencode-free-ai-math.json（格式与 kilo-free-ai-math.json 相同）
    ai_math = []
    for model in free_models:
        model_id = model["id"]
        name = derive_name(model_id)

        config = {
            "id": generate_model_uuid(model_id),
            "modelId": model_id,
            "enableTools": True,
            "disabledTools": [],
            "displayName": f"{name} (OpenCode)",
        }

        reasoning_effort = get_reasoning_effort(model)
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
