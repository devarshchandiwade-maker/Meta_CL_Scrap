from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import re


def parse_facebook_text(text):

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    data = {
        "caption": None,
        "likes": None,
        "comments": None,
        "views": None,
        "date": None,
        "duration": None
    }

    # ====================================
    # FIND VIDEO DURATION
    # ====================================

    duration_index = None

    for i, line in enumerate(lines):

        if re.match(r"\d+:\d+\s*/\s*\d+:\d+", line):

            data["duration"] = line
            duration_index = i
            break

    # ====================================
    # CAPTION
    # ====================================

    if duration_index is not None:

        # caption is usually next line
        if duration_index + 1 < len(lines):

            data["caption"] = lines[duration_index + 1]

    # ====================================
    # LIKES
    # COMMENTS
    # VIEWS
    # ====================================

    for i, line in enumerate(lines):

        # likes
        if re.match(r"^[\d.,KkMm]+$", line):

            # next lines contain comments/views
            nearby = " ".join(lines[i:i+6])

            if "comments" in nearby and "views" in nearby:

                data["likes"] = line

                comments_match = re.search(
                    r'([\d.,KkMm]+)\s+comments',
                    nearby
                )

                views_match = re.search(
                    r'([\d.,KkMm]+)\s+views',
                    nearby
                )

                if comments_match:
                    data["comments"] = comments_match.group(1)

                if views_match:
                    data["views"] = views_match.group(1)

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


# ====================================
# TEST
# ====================================

with open("facebook_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

result = parse_facebook_text(text)

print(result)