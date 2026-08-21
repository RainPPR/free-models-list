"""共用工具函数。"""

import uuid

# 固定命名空间，确保相同 modelId 生成相同 UUID
NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def generate_model_uuid(model_id: str) -> str:
    """根据 modelId 生成确定性的 UUID（uuid5 + DNS namespace）。"""
    return str(uuid.uuid5(NAMESPACE, model_id))
