# services/openai_embeded_service.py

from openai import OpenAI
import logging
import numpy as np
from config.config import OPENAI_API_KEY, SIMILARITY_THRESHOLD

# 設定 OpenAI API Key
openai_client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "text-embedding-3-small"

def get_text_embedding(text: str, model: str = MODEL) -> list:
    """
    將輸入的文字轉換成向量（Embedding）。
    
    Args:
        text (str): 要轉換的文字字串。
        model (str, optional): 使用的模型名稱。預設為 "text-embedding-ada-002"。
    
    Returns:
        list: 生成的向量。
    """
    try:
        response = openai_client.embeddings.create(
            input=text,
            model=model
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"生成 Embedding 時發生錯誤: {e}")
        return []

def compare_embeddings(embedding1: list, embedding2: list, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """
    比較兩個向量的相似度，並檢查是否大於指定的閾值。
    
    Args:
        embedding1 (list): 第一個向量。
        embedding2 (list): 第二個向量。
        threshold (float, optional): 相似度閾值。預設為 config 中的 SIMILARITY_THRESHOLD。
    
    Returns:
        bool: 如果相似度大於閾值，回傳 True；否則回傳 False。
    """
    if not embedding1 or not embedding2:
        print("其中一個或兩個 Embedding 是空的。")
        return False
    
    try:
        # 將列表轉換為 numpy 陣列
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 計算餘弦相似度
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            print("其中一個向量的範數為零，無法計算相似度。")
            return False
        
        cosine_similarity = dot_product / (norm1 * norm2)
        
        return cosine_similarity > threshold
    except Exception as e:
        print(f"計算相似度時發生錯誤: {e}")
        return False