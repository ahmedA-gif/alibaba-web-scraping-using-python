from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
import time
from datetime import datetime

# Setup Chrome
options = Options()
options.add_argument("--start-maximized")
driver_path = "/usr/local/bin/chromedriver"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# URL to scrape
url = "https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y"
driver.get(url)
time.sleep(5)

# CSV setup
filename = "alibaba_rfq_data.csv"
fields = [
    "RFQ ID", "Title", "Buyer Name", "Buyer Image", "Inquiry Time", "Quotes Left",
    "Country", "Quantity Required", "Email Confirmed", "Experienced Buyer",
    "Complete Order via RFQ", "Typical Replies", "Interactive User",
    "Inquiry URL", "Inquiry Date", "Scraping Date"
]

with open(filename, "w", newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fields)

    for page in range(1, 101):
        print(f"Scraping page {page}...")
        time.sleep(3)

        items = driver.find_elements(By.CSS_SELECTOR, ".brh-rfq-item__main-info")
        for item in items:
            try:
                rfq_id = item.get_attribute("data-id") or ""
                title = item.find_element(By.CLASS_NAME, "brh-rfq-item__subject").text.strip()
                buyer_name = item.find_element(By.CLASS_NAME, "brh-rfq-item__buyer-name").text.strip() if item.find_elements(By.CLASS_NAME, "brh-rfq-item__buyer-name") else ""
                buyer_image = item.find_element(By.TAG_NAME, "img").get_attribute("src") if item.find_elements(By.TAG_NAME, "img") else ""
                inquiry_time = ""
                quotes_left = ""
                country = ""
                quantity_required = ""
                email_confirmed = "No"
                experienced_buyer = "No"
                complete_order = "No"
                typical_replies = "No"
                interactive_user = "No"
                inquiry_url = ""
                inquiry_date = ""
                scraping_date = datetime.now().strftime("%Y-%m-%d")

                # Use full text block
                block = item.text.split("\n")
                for line in block:
                    if "Quantity Required" in line:
                        quantity_required = line.split("Quantity Required:")[-1].strip()
                    elif "Posted in:" in line:
                        country = line.split("Posted in:")[-1].strip()
                    elif "Quotes Left" in line:
                        quotes_left = line.split("Quotes Left")[-1].strip()
                    elif "minutes before" in line or "hours before" in line:
                        inquiry_time = line.strip()
                        inquiry_date = datetime.now().strftime("%Y-%m-%d")  # Approx.
                    elif "Email Confirmed" in line:
                        email_confirmed = "Yes"
                    elif "Experienced Buyer" in line:
                        experienced_buyer = "Yes"
                    elif "Complete Order via RFQ" in line:
                        complete_order = "Yes"
                    elif "Typical Replies" in line:
                        typical_replies = "Yes"
                    elif "Interactive User" in line:
                        interactive_user = "Yes"

                try:
                    inquiry_url = item.find_element(By.CLASS_NAME, "brh-rfq-item__subject a").get_attribute("href")
                except:
                    inquiry_url = ""

                writer.writerow([
                    rfq_id, title, buyer_name, buyer_image, inquiry_time, quotes_left, country,
                    quantity_required, email_confirmed, experienced_buyer, complete_order,
                    typical_replies, interactive_user, inquiry_url, inquiry_date, scraping_date
                ])
            except Exception as e:
                print("Error scraping an item:", e)
                continue

        # Pagination
        try:
            if page < 100:
                next_btns = driver.find_elements(By.XPATH, "//a[contains(@href, 'page=')]")
                found = False
                for btn in next_btns:
                    if btn.text.strip() == str(page + 1):
                        driver.execute_script("arguments[0].scrollIntoView();", btn)
                        driver.execute_script("arguments[0].click();", btn)
                        found = True
                        break
                if not found:
                    print(f"Page {page + 1} not found. Ending.")
                    break
        except Exception as e:
            print(f"Pagination error on page {page + 1}: {e}")
            break

driver.quit()
print("✅ Done! Data saved to", filename)
