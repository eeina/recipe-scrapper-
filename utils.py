import re
from typing import Union, Literal
from urllib.parse import urlparse

def parse_time_to_minutes(time_str: Union[str, int, float, None]) -> int:
    """
    Convert a variety of time strings to integer minutes.
    """
    if time_str is None:
        return 0
    if isinstance(time_str, (int, float)):
        return int(round(float(time_str)))
    s = str(time_str).strip().lower()
    if not s:
        return 0
    if s.isdigit():
        return int(s)
    total_minutes = 0.0
    if re.fullmatch(r"\d+:\d{1,2}(?::\d{1,2})?", s):
        parts = [int(p) for p in s.split(":")]
        if len(parts) == 2:
            hours, minutes = parts
            seconds = 0
        else:
            hours, minutes, seconds = parts
        total_minutes = hours * 60 + minutes + (seconds / 60.0)
        return int(round(total_minutes))
    s = s.replace(",", " ")
    s = s.replace("\u2013", "-")
    s = s.replace("\u2014", "-")
    m_iso = re.match(
        r"^pt(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?$", s
    )
    if m_iso:
        h = float(m_iso.group(1)) if m_iso.group(1) else 0.0
        mm = float(m_iso.group(2)) if m_iso.group(2) else 0.0
        sec = float(m_iso.group(3)) if m_iso.group(3) else 0.0
        total_minutes = h * 60.0 + mm + sec / 60.0
        return int(round(total_minutes))
    hour_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|hr|h)\b")
    for m in hour_pattern.finditer(s):
        total_minutes += float(m.group(1)) * 60.0
    minute_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|min|m)\b")
    for m in minute_pattern.finditer(s):
        total_minutes += float(m.group(1))
    second_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(?:seconds?|secs?|sec|s)\b")
    for m in second_pattern.finditer(s):
        total_minutes += float(m.group(1)) / 60.0
    if total_minutes == 0.0:
        compact_hm = re.findall(r"(\d+(?:\.\d+)?)h\s*(\d+(?:\.\d+)?)m", s)
        for h, mm in compact_hm:
            total_minutes += float(h) * 60.0 + float(mm)
        compact_h = re.findall(r"(\d+(?:\.\d+)?)h\b", s)
        for h in compact_h:
            total_minutes += float(h) * 60.0
        compact_m = re.findall(r"(\d+(?:\.\d+)?)m\b", s)
        for mm in compact_m:
            total_minutes += float(mm)
    if total_minutes == 0.0:
        number_pattern = re.search(r"(\d+(?:\.\d+)?)", s)
        if number_pattern:
            total_minutes = float(number_pattern.group(1))
    return int(round(total_minutes))


def parse_servings_to_int(servings_str: Union[str, int, float, None]) -> int:
    """
    Convert various servings/yield formats to integer.
    """
    if servings_str is None:
        return 0
    if isinstance(servings_str, (int, float)):
        return int(round(float(servings_str)))
    s = str(servings_str).strip().lower()
    if not s:
        return 0
    if s.isdigit():
        return int(s)
    range_match = re.search(r"(\d+)\s*[-–—to]\s*(\d+)", s)
    if range_match:
        return int(range_match.group(1))
    number_match = re.search(r"(\d+(?:\.\d+)?)", s)
    if number_match:
        return int(round(float(number_match.group(1))))
    return 0


def get_platform(url: str) -> Literal["tiktok", "youtube", "website"]:
    """
    Detect the platform from URL.
    """
    url_lower = url.lower()
    if "tiktok.com" in url_lower:
        return "tiktok"
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    return "website"
