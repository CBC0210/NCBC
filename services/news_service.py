
from services.news_source.yahoo_news_service import fetch_yahoo_news
from services.news_source.baha_news_service import fetch_baha_news

def get_latest_news():
    news = fetch_yahoo_news()
    # news.extend(fetch_baha_news()) # 版權問題，暫不使用
    return news

