from seleniumbase import Driver
import time
from bs4 import BeautifulSoup
import json

# Initialize the driver
driver = Driver(uc=True)

url = "https://www.careerone.com.au/jobs/in-australia"

# Open URL and handle captcha if needed
driver.uc_open_with_reconnect(url, 4)
driver.uc_gui_click_captcha()
time.sleep(5)

# Function to scroll down gradually
def scroll_down(driver, pause_time=1, scrolls=8):
    for i in range(scrolls):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")  # Scroll one viewport
        time.sleep(pause_time)

# Function to close Google sign-up pop-up if it appears
def close_google_signup(driver):
    try:
        # Adjust the selector based on the actual popup
        popup_close_button = driver.wait_for_element("button[aria-label='Close']", timeout=3)
        if popup_close_button.is_displayed():
            popup_close_button.click()
            print("Google sign-up popup closed.")
    except:
        pass  # Popup didn't appear, continue

# Close popup if it exists
close_google_signup(driver)

# Scroll down the page to load dynamic content
scroll_down(driver, pause_time=1, scrolls=8)

# Extract HTML content
html_content = driver.page_source

# Save HTML
with open('page_content.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML content extracted and saved to page_content.html")
driver.quit()


with open('page_content.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

data = []

soup = BeautifulSoup(html_content, 'html.parser')

job_containers = soup.find_all('div', class_="d-flex flex-column overflow-hidden")

print(f"Found {len(job_containers)} job containers")


for i, div in enumerate(job_containers, 1):
    # Initialize variables for each job
    job_title = ""
    company_name = ""
    location = ""
    salary_range = ""
    # posting_time = ""
    job_description = ""

    h2_title = div.find('h2', class_="text-title-1 text-black text-break leading-6 mb-2")
    if h2_title:
        a_tag = h2_title.find('a')
        job_title = a_tag.get_text(strip=True)
      

    company_div = div.find('h3', class_="text-body-3 text-black mb-0 d-flex")
    if company_div:
        a_tag = company_div.find('a')
        company_name = a_tag.get_text(strip=True)

    location_div = div.find('div', class_="d-inline-block min-h-6 vertical-top text-body-4 text-black text-truncate w-100")
    if location_div:
        a_tag = location_div.find('a')
        if a_tag:
            location = a_tag.get_text(strip=True)
        # else:
        #     posting_time= location_div.get_text(strip=True)

    salary_div = div.find('div', class_="text-body-4 text-black d-flex align-items-center")
    if salary_div:
        span_tag = salary_div.find('span',class_="text-title-4 text-black")
        salary_range = span_tag.get_text(strip=True)
        

    data.append({
        "id": i,
        "job_title": job_title,
        "company_name": company_name,
        "location": location,
        "salary_range": salary_range,
        # "posting_time": posting_time,
        "salary_range": salary_range,
        # "posting_time": posting_time,
        "posted_date": None, # Will be updated in second loop
        "city": parse_location(location)["city"],
        "state": parse_location(location)["state"],
        "country": parse_location(location)["country"],
        "is_remote": False, # Default
        "is_hybrid": False, # Default
        "job_description": job_description,
    })


# ------------- SECOND LOOP: Update posting_time ---------------
posting_containers = soup.find_all('div', class_="d-flex align-items-center col-6")

for i, div in enumerate(posting_containers, 1):
    posting_time_div = div.find('div', class_="text-body-4 flex-shrink-0 mr-3 job-date")
    if posting_time_div:
        posting_time = posting_time_div.get_text(strip=True)

        # update existing entry
        data[i-1]["posted_date"] = parse_posted_date(posting_time)

# ------------- THIRD LOOP: Update Job_description ---------------
job_descrip_containers = soup.find_all('div', class_="d-block cursor-pointer")

for i, div in enumerate(job_descrip_containers, 1):
    # Find the <ul> inside this div
    ul_tag = div.find('ul')
    if ul_tag:
        # Extract all <li> text
        key_points = [li.get_text(strip=True) for li in ul_tag.find_all('li')]
        # Join as single string or keep as list
        key_points_text = "; ".join(key_points)

        # Update existing entry
        if i-1 < len(data):  # safety check
            data[i-1]["job_description"] = key_points_text

  
    
#  Save data to JSON
with open('job_listings.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n--- Summary ---")
print(f"Total jobs extracted: {len(data)}")
print(f"Data saved to job_listings.json")
