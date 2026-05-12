import re
import time
from selenium.webdriver.common.by import By


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

print(extract_facebook_metrics("https://www.facebook.com/reel/24928252270187147"))