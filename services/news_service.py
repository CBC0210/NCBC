from services.news_source.yahoo_news_service import fetch_yahoo_news

def get_latest_news():
    news = fetch_yahoo_news()
    return news