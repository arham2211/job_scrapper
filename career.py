from seleniumbase import Driver
import time
from bs4 import BeautifulSoup
import json
import os
import re
from utils import parse_posted_date, parse_location, parse_salary

# Initialize the driver
driver = Driver(uc=True, headless=True)

url = "https://www.careerone.com.au/jobs/in-australia"

# Open URL and handle captcha if needed
driver.get(url)
# driver.uc_gui_click_captcha() # Optional if needed
time.sleep(5)

# Function to scroll down gradually
def scroll_down(driver, pause_time=1, scrolls=5):
    """Scroll down to load lazy content"""
    for i in range(scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(pause_time)

def close_popups(driver):
    """Close any annoying popups"""
    try:
        # Generic close buttons often found in popups
        selectors = [
            "button[aria-label='Close']",
            ".modal-close",
            "button.close"
        ]
        for sel in selectors:
            try:
                el = driver.find_element("css selector", sel)
                if el.is_displayed():
                    el.click()
                    print(f"Closed popup with selector: {sel}")
            except:
                pass
    except:
        pass

def parse_career_jobs(html):
    soup = BeautifulSoup(html, 'html.parser')
    parsed_jobs = []
    
    # Iterate over job cards
    # Based on browser subagent: .job-card-detailed
    job_cards = soup.select(".job-card-detailed")
    
    for card in job_cards:
        job = {}
        
        # Title
        title_el = card.select_one("h2 a")
        job["job_title"] = title_el.get_text(strip=True) if title_el else None
        job["url"] = None
        if title_el and title_el.has_attr('href'):
            # Ensure absolute URL
            href = title_el['href']
            if href.startswith('/'):
                job["url"] = f"https://www.careerone.com.au{href}"
            else:
                job["url"] = href

        # Company
        company_el = card.select_one("h3 a")
        job["company_name"] = company_el.get_text(strip=True) if company_el else None

        # Location
        # Finds div with location-like text or specific class if available
        # Previous scraper used a somewhat generic locator, let's try to be robust
        # This selector targets the location text usually found under company
        location_el = card.select_one(".text-body-4.text-truncate a") 
        raw_location = location_el.get_text(strip=True) if location_el else None
        job["location"] = raw_location
        
        loc_data = parse_location(raw_location)
        job["city"] = loc_data["city"]
        job["state"] = loc_data["state"] # type: ignore
        job["country"] = loc_data["country"]
        
        # Salary
        # Looking for text that looks like salary
        salary_el = card.find(string=lambda t: t and '$' in t)
        raw_salary = salary_el.strip() if salary_el else None
        # Try a more specific selector if that failed
        if not raw_salary:
             sal_span = card.select_one("span.text-title-4")
             if sal_span:
                 raw_salary = sal_span.get_text(strip=True)

        job["salary_range"] = raw_salary
        min_sal, max_sal = parse_salary(raw_salary)
        job["min_annual_salary"] = min_sal
        job["max_annual_salary"] = max_sal

        # Description / Key Points
        # Often in a UL
        desc_ul = card.select_one("ul")
        if desc_ul:
            points = [li.get_text(strip=True) for li in desc_ul.find_all("li")]
            job["job_description"] = "; ".join(points)
        else:
            job["job_description"] = None
        
        # Work Type
        # Often a badge or text
        work_type = None
        # Look for common work type words
        all_text = card.get_text(" ", strip=True).lower()
        if "full time" in all_text: work_type = "Full time"
        elif "part time" in all_text: work_type = "Part time"
        elif "casual" in all_text: work_type = "Casual"
        elif "contract" in all_text: work_type = "Contract"
        
        job["work_type"] = work_type
        
        # Remote/Hybrid - Check TITLE ONLY as requested
        title_lower = (job["job_title"] or "").lower()
        job["is_remote"] = "remote" in title_lower
        job["is_hybrid"] = "hybrid" in title_lower
        
        job["classification"] = None 

        # Posted Date
        # Look for "2d ago" etc.
        posted_el = card.select_one(".job-date")
        raw_posted = posted_el.get_text(strip=True) if posted_el else None
        job["posted_date"] = parse_posted_date(raw_posted)
        
        parsed_jobs.append(job)
        
    return parsed_jobs


# ==========================================
# MAIN LOOP
# ==========================================

all_jobs = []
max_pages = 5 # Set number of pages to scrape

try:
    # Close popup if it exists
    close_popups(driver)
    
    for page in range(1, max_pages + 1):
        print(f"\n--- Scraping Page {page} ---")
        
        # Scroll to load everything
        scroll_down(driver, pause_time=1, scrolls=5)
        
        # Parse content
        html = driver.page_source
        jobs_on_page = parse_career_jobs(html)
        print(f"  Found {len(jobs_on_page)} jobs")
        all_jobs.extend(jobs_on_page)
        
        if page < max_pages:
            # Go to next page
            try:
                # Based on subagent investigation: button.page-link[aria-label="Go to next page"]
                # Sometimes it might be simple "Next" text or similar
                next_btn = driver.find_element("css selector", "button.page-link[aria-label='Go to next page']")
                
                # Check if disabled
                if not next_btn.is_enabled():
                    print("Next button disabled. Reached end.")
                    break
                    
                # Click
                driver.execute_script("arguments[0].click();", next_btn)
                print("  Clicked Next >")
                time.sleep(5)  # Wait for reload
                
            except Exception as e:
                print(f"  Could not find or click Next button: {e}")
                # Try fallback selector just in case
                try:
                     links = driver.find_elements("css selector", "a.page-link")
                     found_next = False
                     for link in links:
                         if "next" in link.text.lower():
                             link.click()
                             found_next = True
                             print("  Clicked Next (fallback) >")
                             time.sleep(5)
                             break
                     if not found_next:
                         print("  No Next button found (fallback). Stopping.")
                         break
                except:
                     print("  Stopping pagination.")
                     break
                     
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()


print(f"\nTotal jobs collected: {len(all_jobs)}")

# Save JSON
output_dir = "output/career"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "career_jobs.json")

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_jobs, f, indent=2, ensure_ascii=False)

print(f"Saved to {output_file}")
