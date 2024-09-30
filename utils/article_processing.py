import re
from newspaper import Article

def extract_urls_from_text(text):
    url_pattern = re.compile(r'https?://[^\s]+')
    return url_pattern.findall(text)

def fetch_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error fetching article content: {e}")
        return None
