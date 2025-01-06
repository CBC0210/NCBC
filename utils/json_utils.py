import json
import os

def load_json(filepath: str, default_data=None):
    """
    讀取指定的 JSON 檔案，回傳其內容 (dict or list)。
    如果檔案不存在或讀取失敗，就回傳 `default_data`。
    """
    if default_data is None:
        default_data = {}

    if not os.path.exists(filepath):
        return default_data

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[load_json] 讀取 {filepath} 發生錯誤: {e}")
        return default_data

def save_json(filepath: str, data):
    """
    將 data (dict/list) 寫入指定的 JSON 檔案 (覆蓋)。
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[save_json] 寫入 {filepath} 發生錯誤: {e}")
