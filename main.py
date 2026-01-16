import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

KEYWORD = "Service Delivery Manager"
LOCATION = "India"
CHECK_INTERVAL = 1800  # 30 minutes

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

sent_jobs = set()

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "disable_web_page_preview": True}
    requests.post(url, data=data, timeout=10)

def fetch_jobs():
    url = (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={KEYWORD.replace(' ', '%20')}"
        f"&location={LOCATION}&f_TPR=r86400"
    )

    soup = BeautifulSoup(
        requests.get(url, headers=HEADERS, timeout=15).text,
        "html.parser"
    )

    jobs = soup.find_all("div", class_="base-card")
    alerts = []

    for job in jobs:
        title = job.find("h3")
        company = job.find("h4")
        link = job.find("a", href=True)

        if not title or not link:
            continue

        if "service delivery manager" not in title.text.lower():
            continue

        if "under 50 applicants" not in job.get_text(" ").lower():
            continue

        job_key = title.text + link["href"]
        if job_key in sent_jobs:
            continue

        sent_jobs.add(job_key)

        alerts.append(
            f"🚨 LinkedIn Job Alert\n\n"
            f"📌 {title.text.strip()}\n"
            f"🏢 {company.text.strip() if company else 'Unknown'}\n"
            f"👥 Under 50 applicants\n\n"
            f"🔗 {link['href'].split('?')[0]}"
        )

    return alerts

def main():
    send_telegram("✅ LinkedIn Job Alert Bot Started (Railway)")

    while True:
        try:
            for alert in fetch_jobs():
                send_telegram(alert)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            send_telegram(f"⚠️ Error: {e}")
            time.sleep(600)

if __name__ == "__main__":
    main()
