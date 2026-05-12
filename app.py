from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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
def normalize_facebook_url(url):

    reel_match = re.search(r"/reel/(\d+)", url)

    if reel_match:
        video_id = reel_match.group(1)
        return f"https://www.facebook.com/watch/?v={video_id}"

    return url


def extract_facebook_metrics(url):

    url = normalize_facebook_url(url)

    driver = create_driver(headless=True)

    try:

        driver.get(url)

        time.sleep(8)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        text = body_text.lower()

        likes = "Not Found"
        comments = "Not Found"
        shares = "Not Found"
        views = "Not Found"

        # Better regex patterns
        like_patterns = [
            r'([\d\.,]+[kmb]?)\s+likes?',
            r'([\d\.,]+[kmb]?)\s+reactions?'
        ]

        comment_patterns = [
            r'([\d\.,]+[kmb]?)\s+comments?'
        ]

        share_patterns = [
            r'([\d\.,]+[kmb]?)\s+shares?'
        ]

        view_patterns = [
            r'([\d\.,]+[kmb]?)\s+views?'
        ]

        # Find likes
        for pattern in like_patterns:
            match = re.search(pattern, text)
            if match:
                likes = match.group(1)
                break

        # Find comments
        for pattern in comment_patterns:
            match = re.search(pattern, text)
            if match:
                comments = match.group(1)
                break

        # Find shares
        for pattern in share_patterns:
            match = re.search(pattern, text)
            if match:
                shares = match.group(1)
                break

        # Find views
        for pattern in view_patterns:
            match = re.search(pattern, text)
            if match:
                views = match.group(1)
                break

        return {
            "platform": "facebook",
            "url": url,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views
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

    shortcode = url.strip("/").split("/")[-1]
    if len(shortcode) == 0:
        return None
    return shortcode


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