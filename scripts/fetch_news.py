import feedparser
import json
import ollama
import os
from bs4 import BeautifulSoup
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BASE_DIR, "..", "news")

os.makedirs(NEWS_DIR, exist_ok=True)

# -----------------------------
# RSS feeds
# -----------------------------

feeds = [
    "https://spacenews.com/feed",
    "https://www.space.com/feeds/all",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.nasaspaceflight.com/feed/",
    "https://www.esa.int/rssfeed/Our_Activities/Space_Engineering_Technology",
    "https://feeds.arstechnica.com/arstechnica/space",
    "https://payloadspace.com/feed/",
    "https://www.satellitetoday.com/feed/"
]

articles = []
keywords = []

# -----------------------------
# IA FUNCTIONS
# -----------------------------

def analyze_article(text):

    prompt = f"""
    Analyze the following space industry news.

    Return your answer ONLY in valid JSON with this format:

    {{
        "summary": "two sentence summary",
        "category": "Launch | Satellite | Policy | Economy | Science",
        "company": "main company mentioned or Unknown"
    }}

    News:
    {text}
    """

    response = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"]

    try:
        data = json.loads(content)
    except:
        data = {
            "summary": text[:150],
            "category": "Unknown",
            "company": "Unknown"
        }

    return data

# -----------------------------
# IMAGE EXTRACTION
# -----------------------------

def extract_image(html):

    soup = BeautifulSoup(html, "html.parser")

    img = soup.find("img")

    if img and img.get("src"):
        return img["src"]

    return "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/FullMoon2010.jpg/640px-FullMoon2010.jpg"

# -----------------------------
# LOAD OLD ARTICLES
# -----------------------------
posts_path = os.path.join(NEWS_DIR, "posts.json")

if os.path.exists(posts_path):

    with open(posts_path, "r", encoding="utf-8") as f:
        old_articles = json.load(f)

else:
    old_articles = []

# -----------------------------
# FETCH NEWS
# -----------------------------

for url in feeds:

    print("Reading feed:", url)

    feed = feedparser.parse(url)

    for entry in feed.entries[:3]:

        try:

            html_content = entry.summary if "summary" in entry else entry.title

            image = extract_image(html_content)
            clean_text = BeautifulSoup(html_content, "html.parser").get_text()

            analysis = analyze_article(clean_text)

            summary_ai = analysis["summary"]
            category = analysis["category"]
            company = analysis["company"]

            keywords.extend(clean_text.lower().split())

            article = {
                "title": entry.title,
                "summary": summary_ai,
                "link": entry.link,
                "date": entry.get("published", "Unknown"),
                "category": category,
                "company": company,
                "image": image
            }

            articles.append(article)

        except Exception as e:
            print("Error processing article:", e)

# -----------------------------
# MERGE OLD + NEW
# -----------------------------

all_articles = old_articles + articles

# -----------------------------
# REMOVE DUPLICATES
# -----------------------------

unique_articles = []
links_seen = set()

for article in all_articles:

    if article["link"] not in links_seen:

        unique_articles.append(article)
        links_seen.add(article["link"])

# -----------------------------
# LIMIT STORAGE
# -----------------------------

unique_articles = unique_articles[:50]

# -----------------------------
# TRENDS ANALYSIS
# -----------------------------

common_words = Counter(keywords).most_common(10)

trends = []

for word, count in common_words:
    trends.append({
        "keyword": word,
        "count": count
    })

# -----------------------------
# COMPANY RANKING
# -----------------------------

companies = [a["company"] for a in articles if a["company"] != "Unknown"]
ranking = Counter(companies).most_common(5)
company_rank = []

for name, count in ranking:
    company_rank.append({
        "company": name,
        "mentions": count
    })

# -----------------------------
# SAVE FILES
# -----------------------------

with open(os.path.join(NEWS_DIR, "companies.json"), "w", encoding="utf-8") as f:
    json.dump(company_rank,f,indent=2)

with open(os.path.join(NEWS_DIR, "trends.json"), "w", encoding="utf-8") as f:
    json.dump(trends, f, indent=2)

with open(os.path.join(NEWS_DIR, "posts.json"), "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print("Noticias actualizadas con IA")
