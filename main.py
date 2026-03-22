import requests
import json


def main():
    # 请求 API
    url = "https://api.kilo.ai/api/gateway/models"
    response = requests.get(url)
    data = response.json()

    # 定义需要删除的字段
    fields_to_remove = [
        "architecture",
        "top_provider",
        "supported_parameters",
        "settings",
        "default_parameters",
        "preferredIndex",
        "per_request_limits",
        "opencode",
        "versioned_settings"
    ]

    # 遍历所有模型，删除指定字段
    for model in data["data"]:
        for field in fields_to_remove:
            model.pop(field, None)

    # 保存完整的 JSON 到 kilo.json
    with open("kilo.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    # 筛选出 isFree 为 true 的模型
    free_models = []
    for model in data["data"]:
        if model.get("isFree") is True:
            # 复制模型并删除 isFree 和 pricing 字段
            free_model = model.copy()
            free_model.pop("isFree", None)
            free_model.pop("pricing", None)
            free_models.append(free_model)

    # 保存免费模型到 kilo-free.json
    with open("kilo-free.json", "w", encoding="utf-8") as f:
        json.dump(free_models, f, indent=4, ensure_ascii=False)

    print(f"已保存 {len(data['data'])} 个模型到 kilo.json")
    print(f"已保存 {len(free_models)} 个免费模型到 kilo-free.json")


if __name__ == "__main__":
    main()
