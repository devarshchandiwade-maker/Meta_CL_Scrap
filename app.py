from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import instaloader
import re


# ======================================================
# FLASK APP
# ======================================================

app = Flask(__name__)


# ======================================================
# CREATE DRIVER
# ======================================================

def create_driver(headless=True):

    options = Options()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument("--remote-debugging-port=9222")

    options.add_argument(
        "user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # IMPORTANT
    options.binary_location = "/usr/bin/chromium"

    # USE INSTALLED DRIVER
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    return driver
# ======================================================
# FACEBOOK
# ======================================================

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
            "platform": "facebook",
            "likes": likes,
            "comments": comments
        }

    except Exception as e:

        return {
            "platform": "facebook",
            "error": str(e)
        }

    finally:
        driver.quit()


# ======================================================
# INSTAGRAM
# ======================================================

def extract_shortcode(url):

    patterns = [
        r"instagram\.com/reel/([^/?]+)",
        r"instagram\.com/p/([^/?]+)",
        r"instagram\.com/tv/([^/?]+)"
    ]

    for pattern in patterns:

        match = re.search(pattern, url)

        if match:
            return match.group(1)

    return None


def extract_instagram_metrics(url):

    try:

        shortcode = extract_shortcode(url)

        if not shortcode:

            return {
                "platform": "instagram",
                "error": "Invalid Instagram URL"
            }

        # INIT INSTALOADER
        L = instaloader.Instaloader()

        # GET POST
        post = instaloader.Post.from_shortcode(
            L.context,
            shortcode
        )

        return {
            "platform": "instagram",
            "shortcode": shortcode,
            "views": post.video_view_count,
            "likes": post.likes,
            "comments": post.comments,
            "caption": post.caption,
            "date": post.date
        }

    except Exception as e:

        return {
            "platform": "instagram",
            "error": str(e)
        }

# ======================================================
# AUTO DETECT
# ======================================================

def scrape_social_media(url):

    if "facebook.com" in url:
        return extract_facebook_metrics(url)

    elif "instagram.com" in url:
        return extract_instagram_metrics(url)

    else:
        return {
            "error": "Unsupported platform"
        }


# ======================================================
# HOME ROUTE
# ======================================================

@app.route("/")
def home():

    return jsonify({
        "status": "running",
        "message": "Meta Scraper API"
    })


# ======================================================
# SCRAPE ROUTE
# ======================================================

@app.route("/scrape")
def scrape():

    url = request.args.get("url")

    if not url:

        return jsonify({
            "error": "Missing URL parameter"
        })

    result = scrape_social_media(url)

    return jsonify(result)


# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000, debug=True) 