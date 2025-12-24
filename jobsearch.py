from seleniumbase import Driver
import time
from bs4 import BeautifulSoup
import json
import os
from utils import parse_salary, parse_posted_date, parse_location
import re

driver = Driver(uc=True)

base_url = "https://www.jobsearch.com.au/jobs"
base_url_2 = "https://www.jobsearch.com.au/jobs?q=remote"
base_url_3 = "https://www.jobsearch.com.au/jobs?q=hybrid"
data = []

# Determine scan configurations
scans = [
    {"base": base_url},
    {"base": base_url_2},
    {"base": base_url_3}
]

# Iterate through scan configs
for scan in scans:
    current_base = scan["base"]
    
    print(f"\n--- Starting scan for base URL: {current_base} ---")

    # Iterate through pages 1-2 (for testing, or 1-3 etc)
    for page_num in range(1, 2):
        # Handle pagination for URLs that might already have query params
        separator = "&" if "?" in current_base else "?"
        
        if page_num == 1:
            url = current_base
        else:
            url = f"{current_base}{separator}page={page_num}"
        
        print(f"\nScraping page {page_num}: {url}")
        
        # Retry mechanism for navigation
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.uc_open_with_reconnect(url, 4)
                break
            except Exception as e:
                print(f"  Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt == max_retries - 1:
                    print("  Skipping page due to repeated failures.")
                    continue
                
                # Restart driver if needed (some errors might kill it)
                try:
                    driver.quit()
                except:
                    pass
                print("  Restarting driver...")
                time.sleep(2)
                driver = Driver(uc=True)  # Re-initialize driver

        time.sleep(7)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        target_class = (
            "group relative bg-white rounded-xl border transition-all duration-300 "
            "overflow-hidden cursor-pointer w-full border-gray-200 shadow-sm "
            "hover:shadow-md hover:border-indigo-300 hover:-translate-y-0.5"
        )
        li_elements = soup.find_all("li", class_=target_class)

        print(f"  Found {len(li_elements)} job listings")

        # ✅ FIXED: extraction loop MUST BE inside the page loop
        for i, li in enumerate(li_elements, 1):

            job_id = li.get("data-job-id")

            company_span = li.find("span", class_="font-medium truncate min-w-0")
            company_name = company_span.get_text(strip=True) if company_span else None

            h2 = li.find("h2", class_="text-lg font-semibold transition-colors line-clamp-2 mb-2 break-words text-gray-900 group-hover:text-indigo-600")
            job_title = h2.get_text(strip=True) if h2 else None

            # Location
            location = None
            for s in li.find_all("span", class_="truncate"):
                if company_span and s == company_span:
                    continue
                classes = s.get("class", [])
                if "font-medium" in classes or "min-w-0" in classes:
                    continue
                location = s.get_text(strip=True)
                if location:
                    break

            salary_span = li.find("span", class_="px-2.5 py-1 rounded-lg bg-gray-50 text-gray-700 text-xs font-medium border border-gray-200")
            salary_range = salary_span.get_text(strip=True) if salary_span else None

            work = li.find("span", class_="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-medium border border-indigo-100")
            work_type = work.get_text(strip=True) if work else None

            posting_time = None
            # for s in li.find_all("span"):
            #     if s.get("class"):
            #         continue
            #     text = s.get_text(strip=True)
            #     if text:
            #         posting_time = text
            #         break
            for element in li.find_all(string=lambda text: text and "Posted" in text):
                # Get the parent element that contains the full text
                parent = element.parent
                
                # Get all text from this parent element, including child elements
                # Use separator=" " to avoid "Postedyesterday"
                full_text = parent.get_text(separator=" ", strip=True)
                
                # Extract just the time part (remove "Posted" and any extra whitespace)
                if "Posted" in full_text:
                    # Ensure "Posted" is separated
                    posting_time = full_text.replace("Posted", "Posted ").strip()
                    # Clean up multiple spaces if any
                    posting_time = " ".join(posting_time.split())
                    break
                    
            # Remote/Hybrid Detection
            is_remote = False
            is_hybrid = False
            
            title_lower = job_title.lower() if job_title else ""
            if "remote" in title_lower:
                is_remote = True
            if "hybrid" in title_lower:
                is_hybrid = True
                
            loc_data = parse_location(location)

            desc_div = li.find("div", class_="space-y-2 text-sm text-gray-700")
            job_description = desc_div.get_text(separator=" ", strip=True) if desc_div else None

            data.append({
                "job_title": job_title,
                "company_name": company_name,
                "location": location,
                "city": loc_data["city"],
                "state": loc_data["state"],
                "country": loc_data["country"],
                "is_remote": is_remote,
                "is_hybrid": is_hybrid,
                # "classification": None, # REMOVED
                "salary_range": salary_range,
                "min_annual_salary": parse_salary(salary_range)[0],
                "max_annual_salary": parse_salary(salary_range)[1],
                "work_type": work_type,
                # "posting_time": posting_time,
                "posted_date": parse_posted_date(posting_time),
                "job_description": job_description,
                "url": f"https://www.jobsearch.com.au/job/{job_id}" if job_id else None,
            })

driver.quit()

print(f"\nTotal jobs collected: {len(data)}")

os.makedirs("output/jobsearch", exist_ok=True)

with open("output/jobsearch/jobsearch_jobs.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("JSON output saved.")
