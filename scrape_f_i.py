from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re

def extract_fb_metrics(url):
    try:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(url)
        time.sleep(6)

        text = driver.find_element(By.TAG_NAME, "body").text.lower()

        driver.quit()

        # =========================
        # CLEAN + FIND AFTER "PUBLIC"
        # =========================

        words = text.split()

        if "public" in words:
            idx = words.index("public")

            # take next values after "public"
            next_values = words[idx + 1: idx + 10]

            numbers = []

            for w in next_values:
                # keep only numbers like 6.5k, 16k, 3.2k etc
                if re.match(r"^\d+(\.\d+)?[km]?$", w):
                    numbers.append(w)

            likes = numbers[0] if len(numbers) > 0 else "Not Found"
            comments = numbers[1] if len(numbers) > 1 else "Not Found"

        else:
            likes = "Not Found"
            comments = "Not Found"

        return {
            "likes": likes,
            "comments": comments
        }

    except Exception as e:
        return {"error": str(e)}


print(extract_fb_metrics("https://www.facebook.com/reel/950529911097356"))