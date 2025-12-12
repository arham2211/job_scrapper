from seleniumbase import Driver
import time
from bs4 import BeautifulSoup
import json

# Scrape and save HTML
driver = Driver(uc=True)

base_url = "https://www.jobsearch.com.au/jobs"
# Extract data and prepare JSON
data = []

# Iterate through pages 1-30
for page_num in range(1, 3):
    if page_num == 1:
        url = base_url
    else:
        url = f"{base_url}?page={page_num}"
    
    print(f"\nScraping page {page_num}/30: {url}")
    driver.uc_open_with_reconnect(url, 4)
    # driver.uc_gui_click_captcha()
    
    time.sleep(7)
    
    # Extract HTML content from the page
    html_content = driver.page_source
    
    # Extract li classes and content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find li elements with the specific class
    target_class = "group relative bg-white rounded-xl border transition-all duration-300 overflow-hidden cursor-pointer w-full border-gray-200 shadow-sm hover:shadow-md hover:border-indigo-300 hover:-translate-y-0.5"
    li_elements = soup.find_all('li', class_=target_class)
    
    print(f"  Found {len(li_elements)} job listings on page {page_num}")
    
    # Extract data from current page
    for i, li in enumerate(li_elements, 1):
        # Extract job_id from data-job-id attribute
        job_id = li.get('data-job-id')
        
        # Extract span with target class (company name)
        company_span = li.find('span', class_="font-medium truncate min-w-0")
        company_name = company_span.get_text(strip=True) if company_span else None

        # Extract h2 with target class (job title)
        h2 = li.find('h2', class_="text-lg font-semibold transition-colors line-clamp-2 mb-2 break-words text-gray-900 group-hover:text-indigo-600")
        job_title = h2.get_text(strip=True) if h2 else None

        # Extract span(s) with class 'truncate' (location candidates)
        location = None
        for s in li.find_all('span', class_='truncate'):
            # Skip the company span if it also contains 'truncate'
            if company_span is not None and s == company_span:
                continue
            classes = s.get('class', [])
            # Skip spans that are actually company-like (contain font-medium or min-w-0)
            if 'font-medium' in classes or 'min-w-0' in classes:
                continue
            # Prefer spans that are plain 'truncate' (no extra classes)
            location = s.get_text(strip=True)
            if location:
                break

        # Extract span with salary_range class
        salary_span = li.find('span', class_="px-2.5 py-1 rounded-lg bg-gray-50 text-gray-700 text-xs font-medium border border-gray-200")
        salary_range = salary_span.get_text(strip=True) if salary_span else None

        work=li.find('span', class_="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-medium border border-indigo-100")
        work_type = work.get_text(strip=True) if work else None
        # Extract posting_time: first span with no class (skip company and salary spans)
        posting_time = None
        for s in li.find_all('span'):
            if s.get('class') is not None:
                # has class, skip
                continue
            # skip if same as company_span or salary_span
            if company_span is not None and s == company_span:
                continue
            if salary_span is not None and s == salary_span:
                continue
            text = s.get_text(separator=' ', strip=True)
            if text:
                posting_time = text
                break

        # Extract job description div content
        job_description = None
        desc_div = li.find('div', class_="space-y-2 text-sm text-gray-700")
        if desc_div:
            # Use stripped text; if you prefer HTML, use str(desc_div)
            job_description = desc_div.get_text(separator=' ', strip=True)

        # Add to data list (fixed company field name)
        data.append({
            # "id": i,
            "job_title": job_title,
            "company_name": company_name,
            "location": location,
            "classification": None,
            "salary_range": salary_range,
            "work_type": work_type,
            "posting_time": posting_time,
            "job_description": job_description,
            "url": f"https://www.jobsearch.com.au/job/{job_id}" if job_id else None,
        })

# Close the driver after all pages are scraped
driver.quit()

print(f"\nTotal jobs collected: {len(data)}")

# Save to JSON file
import os
os.makedirs("output/jobsearch", exist_ok=True)

with open('output/jobsearch/jobsearch_jobs.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"JSON output saved to output/jobsearch/jobsearch_jobs.json")


