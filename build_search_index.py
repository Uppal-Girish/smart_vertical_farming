import os
from bs4 import BeautifulSoup
import json

# Map URL -> template file and page title
pages = [
    {"url": "/", "template": "index.html", "title": "Home"},
    {"url": "/about-this-project", "template": "about.html", "title": "About This Project"},
    {"url": "/live-data", "template": "live_data.html", "title": "Live Data"},
    {"url": "/health-predictor", "template": "health_predictor.html", "title": "Health Predictor"},
    # Add all your pages here as needed
]

def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        texts = soup.stripped_strings
        full_text = " ".join(texts)
        return full_text

def build_index():
    index = []
    for page in pages:
        template_path = os.path.join("templates", page["template"])
        if os.path.exists(template_path):
            content = extract_text_from_html(template_path)
            index.append({
                "url": page["url"],
                "title": page["title"],
                "content": content
            })
        else:
            print(f"Warning: Template file not found: {template_path}")
    return index

if __name__ == "__main__":
    index = build_index()
    with open("search_index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print("Search index saved to search_index.json")
