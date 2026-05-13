from flask import Flask, request, jsonify

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import time
import instaloader
import re

from yt_dlp import YoutubeDL
from datetime import datetime

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
        return f"https://m.facebook.com/watch/?v={video_id}"

    return url


def parse_facebook_text(text):

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    data = {
        "caption": None,
        "likes": None,
        "comments": None,
        "views": None,
        "date": None,
        "shares": None
    }

    # ====================================
    # CAPTION
    # ====================================

        
    duration_index = None

    for i, line in enumerate(lines):

        # Detect reel duration
        if re.match(r"\d+:\d+\s*/\s*\d+:\d+", line):

            duration_index = i
            break

    if duration_index is not None:

        for j in range(duration_index + 1, len(lines)):

            candidate = lines[j].strip()

            # Skip useless UI words
            skip_words = [
                "like",
                "comment",
                "share",
                "facebook",
                "reels",
                "explore",
                "watch more",
                "log in",
                "create new account"
            ]

            if candidate.lower() in skip_words:
                continue

            # Skip pure numbers
            if re.match(r"^[\d.,KkMm]+$", candidate):
                continue

            # First meaningful text becomes caption
            if len(candidate) > 10:
                data["caption"] = candidate
                break

    # ====================================
    # LIKES COMMENTS VIEWS
    # ====================================

    for i, line in enumerate(lines):

        if re.match(r"^[\d.,KkMm]+$", line):

            nearby = " ".join(lines[i:i+8]).lower()

            if "comments" in nearby or "views" in nearby:

                data["likes"] = line

                comments_match = re.search(
                    r'([\d.,KkMm]+)\s+comments',
                    nearby
                )

                views_match = re.search(
                    r'([\d.,KkMm]+)\s+views',
                    nearby
                )

                shares_match = re.search(
                    r'([\d.,KkMm]+)\s+shares',
                    nearby
                )

                if comments_match:
                    data["comments"] = comments_match.group(1)

                if views_match:
                    data["views"] = views_match.group(1)

                if shares_match:
                    data["shares"] = shares_match.group(1)

                break

    # ====================================
    # DATE
    # ====================================

    date_patterns = [
        r'\d{1,2}\s+[A-Za-z]+\s+at\s+\d{1,2}:\d{2}',
        r'[A-Za-z]+\s+\d{1,2}\s+at\s+\d{1,2}:\d{2}',
    ]

    for line in lines:

        for pattern in date_patterns:

            match = re.search(pattern, line)

            if match:
                data["date"] = match.group(0)
                return data

    return data


def extract_facebook_metrics(url):



    url = normalize_facebook_url(url)

    driver = create_driver(headless=True)

    try:

        driver.get(url)

        time.sleep(8)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(body_text)

        parsed = parse_facebook_text(body_text)
        

        return {
            "all_text": body_text,
            "platform": "facebook",
            "url": url,
            "caption": parsed["caption"],
            "likes": parsed["likes"],
            "comments": parsed["comments"],
            "views": parsed["views"],
            "shares": parsed["shares"],
            "date": parsed["date"]
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

def extract_instagram_metrics(url):

    driver = create_driver(headless=True)

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 20)
        time.sleep(5)

        # =========================
        # LIKES + COMMENTS (your Selenium logic style)
        # =========================
        likes = None
        comments = None

        try:
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "xe9ewy2")
                )
            )

            elements = driver.find_elements(By.CLASS_NAME, "xe9ewy2")

            values = []

            for el in elements:
                text = el.text.strip()
                if text:
                    values.append(text)

            likes = values[0] if len(values) > 0 else None
            comments = values[1] if len(values) > 1 else None

        except:
            pass

        # =========================
        # DATE (your original logic)
        # =========================
        post_date = None
        iso_date = None
        caption = None

        try:
            time_element = driver.find_element(By.TAG_NAME, "time")
            post_date = time_element.text.strip()
            iso_date = time_element.get_attribute("datetime")

            caption_element = driver.find_element(By.CLASS_NAME, "x126k92a")
            caption = caption_element.text.strip()

        except:
            pass

        # =========================
        # VIEWS (Reels)
        # =========================
        views = None

        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text

            match = re.search(r"([\d.,KMkm]+)\s+views", body_text)
            if match:
                views = match.group(1)

        except:
            pass

        return {
            "platform": "instagram",
            "url": url,
            "caption": caption,
            "likes": likes,
            "comments": comments,
            "views": views,
            "datetime": post_date,
            "date": iso_date
        }

    except Exception as e:
        return {
            "platform": "instagram",
            "error": str(e),
            "url": url
        }

    finally:
        driver.quit()
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