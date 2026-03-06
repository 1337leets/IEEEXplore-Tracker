import json
import os
import requests
from datetime import datetime, timedelta
import subprocess

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def fetch_papers(api_key, keyword, max_results, days_back):
    url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"
    start_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y%m%d")
    params = {
        "apikey": api_key,
        "querytext": keyword,
        "start_record": 1,
        "max_records": max_results,
        "start_date": start_date,
        "sort_field": "article_date",
        "sort_order": "desc",
        "output_type": "json"
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return r.json().get("articles", [])
    except Exception as e:
        return []

def save_results(papers_by_keyword, keep_days):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    today = datetime.today().strftime("%Y-%m-%d")
    txt_path = os.path.join(RESULTS_DIR, f"{today}.txt")
    html_path = os.path.join(RESULTS_DIR, f"{today}.html")

    total = 0
    keyword_counts = {}

    # TXT
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"IEEE Tracker — {today}\n")
        f.write("=" * 50 + "\n\n")
        for keyword, papers in papers_by_keyword.items():
            f.write(f"[ {keyword} ]\n\n")
            keyword_counts[keyword] = len(papers)
            if not papers:
                f.write("  Sonuç bulunamadı.\n\n")
                continue
            for p in papers:
                title = p.get("title", "Başlık yok")
                authors = p.get("authors", {}).get("authors", [])
                first_author = authors[0].get("full_name", "?") if authors else "?"
                year = p.get("publication_year", "?")
                link = p.get("html_url", "?")
                f.write(f"  {title}\n")
                f.write(f"  {first_author} et al. ({year})\n")
                f.write(f"  {link}\n\n")
                total += 1
        f.write(f"\nToplam: {total} makale\n")

    # HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IEEE Tracker — {today}</title>
<style>
  body {{ font-family: sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 16px; max-width: 700px; margin: auto; }}
  h1 {{ font-size: 1.1em; color: #90caf9; border-bottom: 1px solid #333; padding-bottom: 8px; }}
  h2 {{ font-size: 0.95em; color: #64b5f6; margin-top: 24px; margin-bottom: 8px; }}
  .paper {{ background: #1e1e1e; border-radius: 8px; padding: 12px; margin-bottom: 10px; }}
  .title {{ font-size: 0.95em; font-weight: bold; margin-bottom: 4px; }}
  .meta {{ font-size: 0.8em; color: #9e9e9e; margin-bottom: 6px; }}
  a {{ color: #90caf9; text-decoration: none; font-size: 0.85em; }}
  a:hover {{ text-decoration: underline; }}
  .empty {{ color: #616161; font-size: 0.85em; }}
  .footer {{ margin-top: 24px; font-size: 0.8em; color: #616161; border-top: 1px solid #333; padding-top: 8px; }}
</style>
</head>
<body>
<h1>IEEE Tracker — {today}</h1>
""")
        for keyword, papers in papers_by_keyword.items():
            f.write(f"<h2>[ {keyword} ]</h2>\n")
            if not papers:
                f.write('<p class="empty">Sonuç bulunamadı.</p>\n')
                continue
            for p in papers:
                title = p.get("title", "Başlık yok")
                authors = p.get("authors", {}).get("authors", [])
                first_author = authors[0].get("full_name", "?") if authors else "?"
                year = p.get("publication_year", "?")
                link = p.get("html_url", "#")
                f.write(f"""<div class="paper">
  <div class="title">{title}</div>
  <div class="meta">{first_author} et al. &nbsp;·&nbsp; {year}</div>
  <a href="{link}" target="_blank">IEEE Xplore →</a>
</div>
""")
        f.write(f'<div class="footer">Toplam {total} makale &nbsp;·&nbsp; {today}</div>\n')
        f.write("</body></html>\n")

    # Rolling window — en eski dosyaları sil
    for ext in [".txt", ".html"]:
        files = sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith(ext)])
        while len(files) > keep_days:
            os.remove(os.path.join(RESULTS_DIR, files[0]))
            files.pop(0)

    return html_path, total, keyword_counts

def send_notification(total, html_path, keyword_counts):
    if total == 0:
        content = "Bugün yeni makale bulunamadı."
    else:
        lines = [f"{k}: {v}" for k, v in keyword_counts.items() if v > 0]
        content = "\n".join(lines)

    subprocess.run([
        "termux-notification",
        "--title", f"IEEE Tracker — {total} yeni makale",
        "--content", content,
        "--action", f"termux-open {html_path}",
        "--id", "ieee-tracker",
        "--priority", "low"
    ])

def main():
    config = load_config()
    api_key = config["api_key"]
    keywords = config["keywords"]
    max_results = config.get("max_results", 5)
    days_back = config.get("days_back", 1)
    keep_days = config.get("keep_days", 7)

    if api_key == "YOUR_API_KEY_HERE":
        print("config.json içindeki api_key alanını doldur.")
        return

    papers_by_keyword = {}
    for kw in keywords:
        papers_by_keyword[kw] = fetch_papers(api_key, kw, max_results, days_back)

    html_path, total, keyword_counts = save_results(papers_by_keyword, keep_days)
    send_notification(total, html_path, keyword_counts)
    print(f"Tamamlandı. {total} makale → {html_path}")

if __name__ == "__main__":
    main()
