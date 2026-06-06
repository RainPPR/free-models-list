#!/usr/bin/env python3
"""
将 kilo-free.json 中的模型生成 AI Math 配置格式的 JSON。
"""

import json
import uuid
from pathlib import Path


def generate_model_uuid(model_id: str) -> str:
    """根据 modelId 生成确定性的 UUID。"""
    # 使用 uuid5（SHA-1 散列）基于固定命名空间和 modelId 生成
    # 确保相同的 modelId 永远生成相同的 UUID
    NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
    return str(uuid.uuid5(NAMESPACE, model_id))


def get_reasoning_effort(model: dict) -> str | None:
    """获取推理努力级别，按照 max -> high -> medium -> low 优先级。"""
    opencode = model.get("opencode", {})
    variants = opencode.get("variants", {})

    if not variants:
        return None

    # 按优先级顺序检查
    priority_order = ["max", "high", "medium", "low"]
    for effort in priority_order:
        if effort in variants:
            return effort

    return None


def generate_ai_math_config(models: list[dict]) -> list[dict]:
    """生成 AI Math 配置。"""
    result = []

    for model in models:
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
            "enableTools": True,  # Kilo 的所有模型都支持工具调用
            "disabledTools": [],
            "displayName": f"{name} (Kilo)",
        }

        # 添加 reasoningEffort 如果存在 variants
        reasoning_effort = get_reasoning_effort(model)
        if reasoning_effort:
            config["reasoningEffort"] = reasoning_effort

        result.append(config)

    return result


def main():
    """主函数。"""
    base_dir = Path(__file__).parent
    json_path = base_dir / "kilo-free.json"
    output_path = base_dir / "kilo-free-ai-math.json"

    if not json_path.exists():
        print(f"错误: 找不到 {json_path}")
        return 1

    with open(json_path, "r", encoding="utf-8") as f:
        models = json.load(f)

    config = generate_ai_math_config(models)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"已生成 AI Math 配置文件: {output_path}")
    print(f"共 {len(config)} 个模型")

    return 0


if __name__ == "__main__":
    exit(main())
