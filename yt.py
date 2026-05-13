from yt_dlp import YoutubeDL
import re
from datetime import datetime

def format_date(upload_date):
    try:
        return datetime.strptime(upload_date, "%Y%m%d").strftime("%Y-%m-%d")
    except:
        return upload_date

def extract_with_ytdlp(url):

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "platform": info.get("extractor"),
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "date": format_date(info.get("upload_date")),
            "description": info.get("description"),
            "duration": info.get("duration"),
            "view_count": (
                info.get("view_count")
                or info.get("play_count")
                or info.get("video_view_count")
            ),
            "like_count": info.get("like_count"),
            "comment_count": info.get("comment_count"),
            "url": url
        }

    except Exception as e:
        return {
            "error": str(e),
            "url": url
        }

print(extract_with_ytdlp("https://www.instagram.com/mxplayer/reel/DUdQA5lDW5R/"))