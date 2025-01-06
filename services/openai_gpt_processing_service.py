# services/openai_processing_service.py
from openai import OpenAI
import os
from config.config import OPENAI_API_KEY, COMMENTATOR_PROMPT, COMMENTATOR_INDEX
import json
from typing import List
import discord

# 設定 OpenAI API Key
openai_client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o-mini"

def clean_content(content: str) -> str:
    """
    使用 OpenAI GPT-4o mini 模型清理內文，移除與新聞內容無關的部分（如廣告）。
    
    Args:
        content (str): 原始新聞內文。
    
    Returns:
        str: 清理後的內文。
    """
    prompt = (
        "請將使用者提供的新聞內文中與主題無關的部分（如廣告、無關段落等）移除，"
        "其他部分維持原文。"
        "除此之外不要輸出其他内容。"
    )
    
    try:
        converted = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "developer", "content": prompt},
                {
                    "role": "user",
                    "content": f"{content}"
                }
            ]
        )
        cleaned_content = converted.choices[0].message.content.strip()
        return cleaned_content
    except Exception as e:
        print(f"清理內文時發生錯誤: {e}")
        return content  # 回傳原始內容作為備援

def generate_new_title(original_title: str, content: str) -> str:
    """
    使用 OpenAI GPT-4o mini 模型生成新的新聞標題，重點在於資訊豐富而非吸引點擊。
    
    Args:
        original_title (str): 原始新聞標題。
        content (str): 清理後的新聞內文。
    
    Returns:
        str: 生成的新標題。
    """
    prompt = (
        "根據以下的新聞標題和內文，生成一個新的標題。"
        "除此之外不要輸出其他内容。"
        "新標題應該能夠提供足夠的資訊，並且避免使用誇張或吸引點擊的詞語。"
    )
    
    try:
        converted = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "developer", "content": prompt},
                {
                    "role": "user",
                    "content": (
                            "\n\n原標題:\n"
                            f"{original_title}"
                            "\n\n內文:\n"
                            f"{content}"
                        )
                }
            ]
        )
        new_title = converted.choices[0].message.content.strip()
        return new_title
    except Exception as e:
        print(f"生成新標題時發生錯誤: {e}")
        return original_title  # 回傳原標題作為備援

def generate_new_content(content: str) -> str:
    """
    使用 OpenAI GPT-4o mini 模型生成新的新聞內文，重點在於易懂、簡潔、無多餘字詞。
    
    Args:
        original_title (str): 原始新聞標題。
        content (str): 清理後的新聞內文。
    
    Returns:
        str: 生成的新內文。
    """
    prompt = (
        "根據以下的新聞內文，生成一個新的內文。"
        "新內文應該易懂、簡潔，並避免使用多餘的字詞和廢話。"
        "重要的詳細資訊仍然要保留，但是可以用分行或簡化或Discord可以渲染的方式呈現。"
        "除此之外不要輸出其他内容。"
    )
    
    try:
        converted = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "developer", "content": prompt},
                {
                    "role": "user",
                    "content": (
                            "\n\n內文:\n"
                            f"{content}"
                        )
                }
            ]
        )
        new_content = converted.choices[0].message.content.strip()
        return new_content
    except Exception as e:
        print(f"生成新內文時發生錯誤: {e}")
        return content  # 回傳原內文作為備援
    
def generate_summary_as_critic(title: str, content: str) -> str:
    """
    使用 OpenAI GPT-4o mini 模型生成評論家的口語描述。

    Args:
        title (str): 新聞標題。
        content (str): 新聞內文。

    Returns:
        str: 生成的評論家描述。
    """
    prompt = COMMENTATOR_PROMPT[COMMENTATOR_INDEX]

    try:
        converted = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "developer", "content": prompt},
                {
                    "role": "user",
                    "content": (
                        f"標題:\n{title}\n\n內文:\n{content}"
                    )
                }
            ]
        )
        summary = converted.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"生成評論家描述時發生錯誤: {e}")
        return "不予置評"  # 回傳預設描述作為備援
    
def determine_tags(tags: List[discord.ForumTag], content: str) -> List[str]:
    """
    使用 OpenAI GPT-4o mini 模型根據內文生成適合的標籤列表。
    
    Args:
        tags (List[discord.ForumTag]): 可用的標籤列表。
        content (str): 清理後的新聞內文。
    
    Returns:
        List[str]: 生成的標籤列表。
    """
    prompt = (
        "根據以下的新聞內文，從提供的標籤列表中選擇適合的標籤（不僅限一個）。"
        "返回一個JSON格式的列表，每個元素是一個標籤。"
        "除此之外不要輸出其他内容，不需要用codeblock框住。"
    )
    
    tag_names = [tag.name for tag in tags]
    tag_list_str = json.dumps(tag_names, ensure_ascii=False)
    
    try:
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "developer", "content": prompt},
                {
                    "role": "user",
                    "content": (
                        f"標籤列表:\n{tag_list_str}\n\n內文:\n{content}"
                    )
                }
            ]
        )
        converted = response.choices[0].message.content.strip()
        print(f"生成標籤: {converted}")
        selected_tags = json.loads(converted)
        return selected_tags
    except Exception as e:
        print(f"生成標籤時發生錯誤: {e}")
        return []

def process_news_file(input_file: str, output_file: str):
    """
    讀取新聞文件，清理每一項的內文，並將結果保存到新的文件中。
    
    Args:
        input_file (str): 輸入的新聞文件路徑。
        output_file (str): 輸出的新聞文件路徑。
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            news_data = json.load(infile)
        
        for item in news_data:
            item['content'] = generate_new_content(item['title'],item['content'])
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            json.dump(news_data, outfile, ensure_ascii=False, indent=4)
        
        print(f"新聞內文已成功清理並保存到 {output_file}")
    except Exception as e:
        print(f"處理新聞文件時發生錯誤: {e}")

# Example usage:
# process_news_file('data/temp_news.json', 'data/temp_news_converted.json')