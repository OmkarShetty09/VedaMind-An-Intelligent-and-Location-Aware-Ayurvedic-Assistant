"""Sun-relative time-of-day classification (kala).

Uses local time + a NOAA-style sunrise approximation when lat/lon are known;
without geolocation it falls back to fixed local-clock windows with an
'approximate' flag so the UI can label it honestly.
"""

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass
class Kala:
    name: str
    local_time: str
    approximate: bool = False


def approx_sunrise(d: date, lat: float, lon: float, tz_offset_hours: float) -> time:
    """NOAA-style solar calculation. Accuracy ~2-4 minutes, adequate for wellness."""
    n = d.timetuple().tm_yday
    decl = math.radians(-23.44) * math.cos(math.radians(360 / 365 * (n + 10)))
    lat_r = math.radians(lat)
    cos_h = -math.tan(lat_r) * math.tan(decl)
    cos_h = max(-1.0, min(1.0, cos_h))
    hour_angle = math.degrees(math.acos(cos_h))
    solar_noon_utc = 12.0 - lon / 15.0
    sunrise_utc = solar_noon_utc - hour_angle / 15.0
    local = (sunrise_utc + tz_offset_hours) % 24
    h = int(local)
    m = int(round((local - h) * 60)) % 60
    return time(h, m)


def classify(local_dt: datetime, sunrise=None, sunset=None) -> Kala:
    t = local_dt.time()
    if sunrise and sunset:
        # brahma muhurta = 96 minutes before sunrise
        muhurta_start = (sunrise - timedelta(minutes=96)).time()
        if muhurta_start <= t < sunrise:
            return Kala("brahma_muhurta", t.strftime("%H:%M"))
        if sunrise <= t < _add_minutes(sunrise, 60):
            return Kala("sunrise", t.strftime("%H:%M"))
        if t < time(12, 0):
            return Kala("mid_morning", t.strftime("%H:%M"))
        if t < time(14, 0):
            return Kala("midday", t.strftime("%H:%M"))
        if t < time(17, 0):
            return Kala("afternoon", t.strftime("%H:%M"))
        if sunset <= t < _add_minutes(sunset, 60):
            return Kala("sunset", t.strftime("%H:%M"))
        if t < time(22, 0):
            return Kala("evening", t.strftime("%H:%M"))
        return Kala("night", t.strftime("%H:%M"))

    # No sun data: conservative clock-based fallback, flagged approximate.
    approx = Kala("", t.strftime("%H:%M"), approximate=True)
    if 4 <= t.hour < 6:
        approx.name = "brahma_muhurta"
    elif t.hour < 9:
        approx.name = "sunrise"
    elif t.hour < 12:
        approx.name = "mid_morning"
    elif t.hour < 14:
        approx.name = "midday"
    elif t.hour < 17:
        approx.name = "afternoon"
    elif t.hour < 19:
        approx.name = "sunset"
    elif t.hour < 22:
        approx.name = "evening"
    else:
        approx.name = "night"
    return approx


def _add_minutes(t: time, minutes: int) -> time:
    return (datetime.combine(datetime.today(), t) + timedelta(minutes=minutes)).time()
