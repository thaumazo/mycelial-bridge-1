import re
from newspaper import Article

def extract_urls_from_text(text):
    # Extract URL inside angle brackets, and ensure no trailing `>`
    url_pattern = re.compile(r'<(https?://[^\s>]+)>')
    urls = url_pattern.findall(text)
    # Remove any potential trailing characters like '>'
    return [url.rstrip('>') for url in urls]

def fetch_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error fetching article content: {e}")
        return None
