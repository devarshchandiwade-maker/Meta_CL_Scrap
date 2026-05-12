from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

import time
import re


# ==========================================
# CREATE DRIVER
# ==========================================

def create_driver(headless=True):
    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    return driver


# ==========================================
# FACEBOOK SCRAPER
# ==========================================

def extract_facebook_metrics(url):
    driver = create_driver(headless=True)

    try:
        driver.get(url)

        time.sleep(6)

        body_text = driver.find_element(By.TAG_NAME, "body").text.lower()

        words = body_text.split()

        likes = "Not Found"
        comments = "Not Found"

        if "public" in words:
            idx = words.index("public")

            next_values = words[idx + 1: idx + 15]

            numbers = []

            for word in next_values:

                if re.match(r"^\d+(\.\d+)?[km]?$", word):
                    numbers.append(word)

            if len(numbers) > 0:
                likes = numbers[0]

            if len(numbers) > 1:
                comments = numbers[1]

        return {
            "platform": "Facebook",
            "likes": likes,
            "comments": comments
        }

    except Exception as e:
        return {
            "platform": "Facebook",
            "error": str(e)
        }

    finally:
        driver.quit()


# ==========================================
# INSTAGRAM SCRAPER
# ==========================================

def extract_instagram_metrics(url):
    driver = create_driver(headless=False)

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 20)

        wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "xe9ewy2")
            )
        )

        time.sleep(3)

        elements = driver.find_elements(By.CLASS_NAME, "xe9ewy2")

        values = []

        for el in elements:
            text = el.text.strip()

            if text:
                values.append(text)

        likes = values[0] if len(values) > 0 else "Not Found"
        comments = values[1] if len(values) > 1 else "Not Found"

        # =========================
        # POST DATE
        # =========================

        try:
            time_element = driver.find_element(By.TAG_NAME, "time")

            post_date = time_element.text.strip()

            datetime_value = time_element.get_attribute("datetime")

        except Exception:
            post_date = "Not Found"
            datetime_value = "Not Found"

        return {
            "platform": "Instagram",
            "likes": likes,
            "comments": comments,
            "post_date": post_date,
            "datetime": datetime_value
        }

    except Exception as e:
        return {
            "platform": "Instagram",
            "error": str(e)
        }

    finally:
        driver.quit()


# ==========================================
# AUTO DETECT PLATFORM
# ==========================================

def scrape_social_media(url):

    if "facebook.com" in url:
        return extract_facebook_metrics(url)

    elif "instagram.com" in url:
        return extract_instagram_metrics(url)

    else:
        return {
            "error": "Unsupported platform"
        }


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    urls = [
        "https://www.facebook.com/reel/950529911097356",
        "https://www.instagram.com/reel/DXBB07DjAtr/"
    ]

    for url in urls:

        print("\n====================================")
        print("URL:", url)

        result = scrape_social_media(url)

        for key, value in result.items():
            print(f"{key.capitalize():12}: {value}")

        print("====================================")