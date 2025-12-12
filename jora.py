from seleniumbase import Driver
from bs4 import BeautifulSoup
import json
import time
import re


def extract_badges(soup):
    # Collect ALL badge types you care about
    badge_selectors = [
        "div.badge.-default-badge .content",
        "div.badge.-work-arrangement-badge .content"
    ]

    badges = []
    for sel in badge_selectors:
        for b in soup.select(sel):
            text = b.get_text(strip=True)
            if text:
                badges.append(text)

    salary = None
    work_types = []

    for text in badges:
        lower = text.lower()

        # Filter nonsense
        if text in ["badge", ""]:
            continue

        # Salary detection
        if "$" in text or re.search(r"\d", text):
            salary = text
            continue

        # Everything else = work type
        work_types.append(text)

    return salary, work_types




# -----------------------------------------
# Extract fields from the NEW website
# -----------------------------------------
def parse_new_site(html):
    soup = BeautifulSoup(html, "html.parser")
    job = {}

    # Job Title
    title_el = soup.find("h1", class_="job-title")
    job["job_title"] = title_el.get_text(strip=True) if title_el else None

    # Advertiser name
    advertiser_el = soup.find("span", class_="company")
    job["advertiser_name"] = advertiser_el.get_text(strip=True) if advertiser_el else None

    # Location
    location_el = soup.find("span", class_="location")
    job["location"] = location_el.get_text(strip=True) if location_el else None


    salary, work_types = extract_badges(soup)

    job["salary"] = salary
    job["work_type"] = work_types


    # Posted date
    posted_el = soup.select_one("#job-meta .listed-date")
    job["posted"] = posted_el.get_text(strip=True) if posted_el else None

    # FULL job description
    desc_container = soup.find("div", id="job-description-container")
    if desc_container:
        text = desc_container.get_text("\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        job["job_description"] = "\n".join(lines)
    else:
        job["job_description"] = None

    return job


# -----------------------------------------
# SCRAPER PIPELINE
# -----------------------------------------

LISTING_URL = "https://au.jora.com/Data-Sql-jobs?sp=trending_popular"

driver = Driver(uc=True, headless=True)
driver.get(LISTING_URL)
time.sleep(4)

# Extract job links
elements = driver.find_elements("css selector", "a.job-link.show-job-description")

job_urls = []
for el in elements:
    href = el.get_attribute("href")
    if href:
        job_urls.append(href)

print(f"Found {len(job_urls)} job URLs")


# -----------------------------------------
# Fetch each job & parse
# -----------------------------------------

jobs_output = []

for index, url in enumerate(job_urls, start=1):
    print(f"[{index}/{len(job_urls)}] Fetching: {url}")
    
    driver.get(url)
    time.sleep(3)

    html = driver.execute_script("return document.documentElement.outerHTML")
    parsed = parse_new_site(html)
    parsed["url"] = url

    jobs_output.append(parsed)

driver.quit()

# Save JSON
with open("new_site_jobs.json", "w", encoding="utf-8") as f:
    json.dump(jobs_output, f, indent=2, ensure_ascii=False)

print("Saved to new_site_jobs.json")
