import feedparser
import json
import os
import random
from bs4 import BeautifulSoup
from collections import Counter
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(BASE_DIR, "..", "news")

os.makedirs(NEWS_DIR, exist_ok=True)

default_images = [
    "https://upload.wikimedia.org/wikipedia/commons/9/91/Starlink_Mission_%2847926144123%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Earth_flag_PD.jpg/960px-Earth_flag_PD.jpg",
    "https://c.files.bbci.co.uk/85C7/production/_104574243_gettyimages-182062885.jpg",
    "https://media.istockphoto.com/id/498697432/es/foto/sat%C3%A9lite-en-el-espacio.jpg?s=612x612&w=0&k=20&c=iJrHcII0MRP0udk2scj8Iuky78-CQtoQD7Ih3ddx80w=",
    "https://www.esa.int/var/esa/storage/images/esa_multimedia/images/2016/08/sharp_eyes_on_earth/16092893-1-eng-GB/Sharp_eyes_on_Earth_article.jpg"
]

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

    Return ONLY JSON:

    {{
    "summary": "two sentences",
    "category": "Launch | Satellite | Policy | Economy | Science | Mission | History",
    "company": "main company or organization mentioned"
    }}

    News:
    {text}
    """

    try:
        response = client.chat(
            model="mistral-small-latest",
            messages=[ChatMessage(role="user", content=prompt)]
        )

        content = response.choices[0].message.content

        start = content.find("{")
        end = content.rfind("}") + 1

        if start == -1 or end == -1:
            raise ValueError("No JSON found")

        return json.loads(content[start:end])

    except Exception as e:
        print("Mistral error:", e)

        return {
            "summary": text[:150],
            "category": "Unknown",
            "company": "Unknown"
        }


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
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url", "")

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

    # 5 imagen por defecto aleatoria
    return random.choice(default_images)

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

    for entry in feed.entries[:10]:

        try:

            html_content = entry.summary if "summary" in entry else entry.title

            image = extract_image(entry)
            clean_text = entry.title + " " + BeautifulSoup(html_content, "html.parser").get_text()

            analysis = analyze_article(clean_text)

            company = detect_company_keywords(clean_text)

            if company is None:

                company = analysis["company"]
                company = company.strip()

            summary_ai = analysis["summary"]
            category = analysis["category"]

            stopwords = {"the","and","to","of","in","a","for","on","with"}

            keywords.extend([
                w for w in clean_text.lower().split()
                if w not in stopwords and len(w) > 3
            ])

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

companies = [
    a["company"] for a in articles
    if a["company"] 
    and a["company"].lower() not in ["unknown", "null", ""]
]
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
