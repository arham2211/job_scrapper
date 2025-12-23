from seleniumbase import Driver
from bs4 import BeautifulSoup
import json
import time
import re
import os
from utils import parse_posted_date, parse_location, parse_salary


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
        # Filter nonsense
        if text.lower() in ["badge", ""]:
            continue

        # Salary detection
        if "$" in text or re.search(r"\d", text):
            # rudimentary check, sometimes digits might be in other things, but usually OK for badges
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

    # Company name (previously advertiser_name)
    advertiser_el = soup.find("span", class_="company")
    job["company_name"] = advertiser_el.get_text(strip=True) if advertiser_el else None

    # Location
    location_el = soup.find("span", class_="location")
    raw_location = location_el.get_text(strip=True) if location_el else None
    job["location"] = raw_location
    
    loc_data = parse_location(raw_location)
    job["city"] = loc_data["city"]
    job["state"] = loc_data["state"] # type: ignore
    job["country"] = loc_data["country"]
    
    # Remote/Hybrid defaults - could be improved if scraped from badges or description
    job["is_remote"] = False
    job["is_hybrid"] = False

    salary, work_types = extract_badges(soup)

    job["salary_range"] = salary
    min_sal, max_sal = parse_salary(salary)
    job["min_annual_salary"] = min_sal
    job["max_annual_salary"] = max_sal
    
    job["work_type"] = ", ".join(work_types) if work_types else None
    job["classification"] = None  # Jora doesn't easily expose this in the same way

    # Posted date
    posted_el = soup.select_one("#job-meta .listed-date")
    raw_posted = posted_el.get_text(strip=True) if posted_el else None
    job["posted_date"] = parse_posted_date(raw_posted)

    # FULL job description
    desc_container = soup.find("div", id="job-description-container")
    if desc_container:
        text = desc_container.get_text("\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        job["job_description"] = "\n".join(lines)
        
        # Simple extraction for remote/hybrid from description if needed
        desc_lower = job["job_description"].lower()
        if "remote" in desc_lower:
            job["is_remote"] = True
        if "hybrid" in desc_lower or "hybrid" in (job["work_type"] or "").lower():
            job["is_hybrid"] = True
    else:
        job["job_description"] = None

    return job


# -----------------------------------------
# SCRAPER PIPELINE
# -----------------------------------------

base_url = "https://au.jora.com/jobs-in-Berwick-VIC?sp=browse"

driver = Driver(uc=True, headless=True)

job_urls = []

# Pagination loop
# Iterating pages 1-3 for demonstration/initial run. 
# Adjust range as needed (e.g., range(1, 10))
for page_num in range(1, 4):
    if page_num == 1:
        current_url = base_url
    else:
        current_url = f"{base_url}&p={page_num}"
        
    print(f"\nScraping page {page_num}: {current_url}")
    
    driver.get(current_url)
    time.sleep(4)

    # Extract job links
    elements = driver.find_elements("css selector", "a.job-link.show-job-description")
    
    found_urls = []
    for el in elements:
        href = el.get_attribute("href")
        if href:
            found_urls.append(href)
            
    print(f"  Found {len(found_urls)} jobs on page {page_num}")
    job_urls.extend(found_urls)


print(f"\nTotal job URLs collected: {len(job_urls)}")


# -----------------------------------------
# Fetch each job & parse
# -----------------------------------------

jobs_output = []

for index, url in enumerate(job_urls, start=1):
    print(f"[{index}/{len(job_urls)}] Fetching: {url}")
    
    try:
        driver.get(url)
        time.sleep(3)

        html = driver.execute_script("return document.documentElement.outerHTML")
        parsed = parse_new_site(html)
        parsed["url"] = url

        jobs_output.append(parsed)
    except Exception as e:
        print(f"Error fetching {url}: {e}")

driver.quit()

# Save JSON
output_dir = "output/jora"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "jora_jobs.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(jobs_output, f, indent=2, ensure_ascii=False)

print(f"Saved {len(jobs_output)} jobs to {output_file}")
