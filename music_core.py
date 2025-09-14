# music_core.py
import os
import yt_dlp as ytdl
from collections import deque
from pathlib import Path

TMP = Path("./downloads")
TMP.mkdir(exist_ok=True)

YTDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": str(TMP / "%(id)s.%(ext)s"),
    "noplaylist": True,
    "quiet": True,
    "no_warnings": True,
    "cachedir": False,
}

ydl = ytdl.YoutubeDL(YTDL_OPTS)

queues = {}  # chat_id -> deque

def download_audio(query: str):
    # إذا كان رابطًا سيحمله، وإلا يبحث في يوتيوب
    try:
        info = ydl.extract_info(query, download=True)
    except Exception:
        with ytdl.YoutubeDL({"format":"bestaudio","quiet":True, "default_search":"ytsearch", "noplaylist":True, "outtmpl": str(TMP / "%(id)s.%(ext)s")}) as y:
            info = y.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
    filename = ydl.prepare_filename(info)
    return {
        "id": info.get("id"),
        "title": info.get("title"),
        "filepath": filename,
        "duration": info.get("duration"),
        "webpage_url": info.get("webpage_url"),
    }

def add_to_queue(chat_id: int, item):
    q = queues.setdefault(chat_id, deque())
    q.append(item)
    return len(q)

def get_queue(chat_id: int):
    return list(queues.get(chat_id, []))

def pop_queue(chat_id: int):
    q = queues.get(chat_id)
    if not q:
        return None
    return q.popleft()