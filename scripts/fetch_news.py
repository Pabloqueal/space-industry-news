import feedparser
import json
import ollama
from bs4 import BeautifulSoup
from collections import Counter

feeds = [
    "https://spacenews.com/feed",
    "https://www.nasa.gov/rss/dyn/breaking_news.rss",
    "https://www.esa.int/rssfeed/Our_Activities/Space_Engineering_Technology"
]

articles = []

def summarize(text):

    prompt = f"""
    Summarize the following space industry news in 2 concise sentences.
    Focus on the key event and why it matters.

    Article:
    {text}
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]

def classify(text):

    prompt = f"""
    Classify this space news into ONE category:
    Launch
    Satellite
    Policy
    Economy
    Science

    News:
    {text}

    Return only the category name.
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"].strip()

def detect_company(text):

    prompt = f"""
    Identify the space company mentioned in this news.
    If none is mentioned return 'Unknown'.

    News:
    {text}

    Return only the company name.
    """

    response = ollama.chat(
        model="llama3",
        messages=[{"role":"user","content":prompt}]
    )

    return response["message"]["content"].strip()

def extract_image(html):

    soup = BeautifulSoup(html, "html.parser")

    img = soup.find("img")

    if img and img.get("src"):
        return img["src"]

    return "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/FullMoon2010.jpg/640px-FullMoon2010.jpg"

keywords = []

for url in feeds:

    feed = feedparser.parse(url)

    for entry in feed.entries[:3]:

        image = extract_image(entry.summary)
        clean_text = BeautifulSoup(entry.summary, "html.parser").get_text()
        summary_ai = summarize(clean_text)
        category = classify(clean_text)
        company = detect_company(clean_text)
        keywords.extend(clean_text.lower().split())

        article = {
            "title": entry.title,
            "summary": summary_ai,
            "link": entry.link,
            "date": entry.published,
            "category": category,
            "company": company,
            "image": image
        }

        articles.append(article)

common_words = Counter(keywords).most_common(10)
companies = [a["company"] for a in articles if a["company"] != "Unknown"]
ranking = Counter(companies).most_common(5)

trends = []
for word, count in common_words:
    trends.append({
        "keyword": word,
        "count": count
    })

company_rank = []
for name, count in ranking:
    company_rank.append({
        "company": name,
        "mentions": count
    })

with open("../news/companies.json","w") as f:
    json.dump(company_rank,f,indent=2)

with open("../news/trends.json", "w", encoding="utf-8") as f:
    json.dump(trends, f, indent=2)

with open("../news/posts.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)


print("Noticias resumidas con IA y actualizadas")