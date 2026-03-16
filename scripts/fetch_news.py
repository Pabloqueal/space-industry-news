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

    Return ONLY valid JSON with this structure:

    {{
    "summary": "two sentence summary",
    "category": "Launch | Satellite | Policy | Economy | Science | Mission | History",
    "company": "main organization or company mentioned (examples: SpaceX, NASA, ESA, Rocket Lab, Blue Origin). If none is clearly mentioned return Unknown"
    }}

    News:
    {text}
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["message"]["content"].strip()

    start = content.find("{")
    end = content.rfind("}") + 1

    content = content[start:end]

    try:
        data = json.loads(content)
    except:
        data = {
            "summary": text[:150],
            "category": "Unknown",
            "company": "Unknown"
        }

    return data


def detect_company_keywords(text):

    companies = [
        "SpaceX",
        "NASA",
        "ESA",
        "Rocket Lab",
        "Blue Origin",
        "Northrop Grumman",
        "Boeing",
        "Lockheed Martin"
    ]

    for c in companies:
        if c.lower() in text.lower():
            return c

    return None

# -----------------------------
# IMAGE EXTRACTION
# -----------------------------

def extract_image(entry):

    # 1 media_content (muchos RSS)
    if "media_content" in entry:
        return entry.media_content[0]["url"]

    # 2 media_thumbnail
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]

    # 3 enclosure
    if "links" in entry:
        for link in entry.links:
            if link.get("type","").startswith("image"):
                return link["href"]

    # 4 buscar <img> en HTML
    if "summary" in entry:
        soup = BeautifulSoup(entry.summary,"html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    # 5 imagen por defecto
    return "https://upload.wikimedia.org/wikipedia/commons/2/2d/Meteosat-12-fci-march-equinox-2025-noon.jpg"

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

    for entry in feed.entries[:5]:

        try:

            html_content = entry.summary if "summary" in entry else entry.title

            image = extract_image(entry)
            clean_text = entry.title + " " + BeautifulSoup(html_content, "html.parser").get_text()

            analysis = analyze_article(clean_text)

            company = detect_company_keywords(clean_text)

            if company is None:

                company = analysis["company"]

            summary_ai = analysis["summary"]
            category = analysis["category"]

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
