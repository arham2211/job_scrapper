from seleniumbase import Driver
from bs4 import BeautifulSoup
import time
import json
import re

def safe_extract(soup, selector):
    el = soup.find(attrs={"data-automation": selector})
    return el.get_text(strip=True) if el else None

def extract_job_details(html):
    soup = BeautifulSoup(html, "html.parser")

    job = {}

    job["job_title"] = safe_extract(soup, "job-detail-title")
    job["company_name"] = safe_extract(soup, "advertiser-name")
    job["location"] = safe_extract(soup, "job-detail-location")
    job["classification"] = safe_extract(soup, "job-detail-classifications")
    job["work_type"] = safe_extract(soup, "job-detail-work-type")
    job["salary_range"] = safe_extract(soup, "job-detail-salary")

    # Posted date (no unique selector)
    posted_tag = soup.find("span", string=re.compile(r"Posted\s+\d+[hdw]"))
    job["posting_time"] = posted_tag.get_text(strip=True) if posted_tag else None

    # Job description
    details_div = soup.find("div", attrs={"data-automation": "jobAdDetails"})
    if details_div:
        text = details_div.get_text("\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        job["job_description"] = "\n".join(lines)
    else:
        job["job_description"] = None

    return job


# =======================================
# MASTER PIPELINE
# =======================================

BASE_URL = "https://www.seek.com.au/jobs/in-Brisbane-QLD-4000?classification=6251%2C1200%2C6304%2C1203%2C1204%2C1225%2C6246%2C6261%2C1223%2C6362%2C6043%2C1220%2C6058%2C6008%2C6092%2C1216%2C1214%2C6281%2C6317%2C1212%2C1211%2C1210%2C6205%2C1209%2C6123%2C6263%2C6076%2C1206%2C6163%2C7019&subclassification=6252%2C6253%2C6254%2C6255%2C6256%2C6257%2C6258%2C6259%2C6260"

# https://www.seek.com.au/jobs/in-Brisbane-QLD-4000?classification=6251%2C1200%2C6304%2C1203%2C1204%2C1225%2C6246%2C6261%2C1223%2C6362%2C6043%2C1220%2C6058%2C6008%2C6092%2C1216%2C1214%2C6281%2C6317%2C1212%2C1211%2C1210%2C6205%2C1209%2C6123%2C6263%2C6076%2C1206%2C6163%2C7019&page=2&subclassification=6252%2C6253%2C6254%2C6255%2C6256%2C6257%2C6258%2C6259%2C6260

driver = Driver(uc=True, headless=True)

job_urls = []

# Iterate through pages 1-20
for page_num in range(1, 21):
    if page_num == 1:
        listing_url = BASE_URL
    else:
        listing_url = f"{BASE_URL}&page={page_num}"
    
    print(f"Scraping page {page_num}/20: {listing_url}")
    driver.get(listing_url)
    time.sleep(5)
    
    # Extract job listing URLs from current page
    elements = driver.find_elements("css selector", "a[data-testid='job-list-item-link-overlay']")
    
    page_job_urls = []
    for el in elements:
        href = el.get_attribute("href")
        if href:
            page_job_urls.append(href)
    
    job_urls.extend(page_job_urls)
    print(f"  Found {len(page_job_urls)} job URLs on page {page_num}")

print(f"\nTotal job URLs collected: {len(job_urls)}")


# =======================================
# VISIT EACH JOB & PARSE IT
# =======================================

all_jobs = []

for index, url in enumerate(job_urls, start=1):
    print(f"[{index}/{len(job_urls)}] Fetching: {url}")

    driver.get(url)
    time.sleep(3)

    html = driver.execute_script("return document.documentElement.outerHTML")

    job_data = extract_job_details(html)
    job_data["url"] = url

    all_jobs.append(job_data)


driver.quit()


# =======================================
# SAVE JSON
# =======================================

import os
os.makedirs("output/seek", exist_ok=True)

with open("output/seek/seek_jobs.json", "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print("Saved output to output/seek/seek_jobs.json")
